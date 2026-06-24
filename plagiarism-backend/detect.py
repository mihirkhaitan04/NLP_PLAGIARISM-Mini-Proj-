import os
import numpy as np
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from web_scraper import get_web_references
from ai_detector import detect_ai_content

load_dotenv()

HF_API_TOKEN = os.getenv("HF_API_TOKEN")

# Hugging Face hosted multilingual embedding model (supports 50+ languages)
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDING_URL = f"https://router.huggingface.co/hf-inference/models/{EMBEDDING_MODEL}/pipeline/feature-extraction"

HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"}

# This is your local reference database - texts to compare against (offline fallback)
REFERENCE_TEXTS = [
    "Artificial intelligence has revolutionised the way we process information in modern systems.",
    "Machine learning models are trained on large datasets to make predictions.",
    "Plagiarism is the act of using someone else's work without giving proper credit.",
    "Deep learning uses neural networks with many layers to learn complex patterns.",
    "Natural language processing helps computers understand and generate human language.",
]


def get_embeddings(texts):
    """
    Get embeddings for a list of texts using the Hugging Face Inference API.
    Returns a list of embedding vectors (each is a list of floats).
    """
    if isinstance(texts, str):
        texts = [texts]

    payload = {
        "inputs": texts,
        "options": {"wait_for_model": True}
    }
    try:
        response = requests.post(EMBEDDING_URL, headers=HEADERS, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[Warn] Embedding API call failed: {e}")
        return None


def cosine_similarity(vec_a, vec_b):
    """Calculate cosine similarity between two vectors using numpy."""
    a = np.array(vec_a)
    b = np.array(vec_b)
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot / (norm_a * norm_b))


def detect_plagiarism(input_text):
    """Original offline-only detection (kept as fallback)."""
    sentences = [s.strip() for s in input_text.split('.') if s.strip()]
    if not sentences:
        return {"overall_score": 0, "ai_generated_score": 0, "paraphrased_score": 0, "ai_detection_details": {}, "status": "done", "flagged_sections": []}

    flagged_sections = []
    total_score = 0

    # Get embeddings for all sentences + all references in one batch call
    all_texts = sentences + REFERENCE_TEXTS
    all_embeddings = get_embeddings(all_texts)

    if all_embeddings is None or len(all_embeddings) != len(all_texts):
        # Fallback: return empty results if API fails
        return {"overall_score": 0, "ai_generated_score": 0, "paraphrased_score": 0, "ai_detection_details": {}, "status": "error", "flagged_sections": []}

    sentence_embeddings = all_embeddings[:len(sentences)]
    ref_embeddings = all_embeddings[len(sentences):]

    for i, sentence in enumerate(sentences):
        best_score = 0
        for j in range(len(REFERENCE_TEXTS)):
            similarity = cosine_similarity(sentence_embeddings[i], ref_embeddings[j])
            if similarity > best_score:
                best_score = similarity

        total_score += best_score

        if best_score > 0.5:
            flagged_sections.append({
                "start": input_text.find(sentence),
                "end": input_text.find(sentence) + len(sentence),
                "text": sentence,
                "type": "paraphrased",
                "confidence": round(best_score, 2),
                "source": "local_database",
                "source_url": None,
                "source_title": "Local Reference Database"
            })

    overall_score = round((total_score / len(sentences)) * 100, 1) if sentences else 0

    # --- AI Content Detection ---
    ai_result = detect_ai_content(input_text)
    ai_generated_score = ai_result["ai_probability"]

    return {
        "overall_score": overall_score,
        "ai_generated_score": ai_generated_score,
        "paraphrased_score": round(overall_score * 0.4, 1),
        "ai_detection_details": ai_result,
        "status": "done",
        "flagged_sections": flagged_sections
    }


def _process_chunk(chunk, ref_embeddings):
    print(f"  [Search] Thread searching web for: \"{chunk[:60]}...\"")
    chunk_emb_result = get_embeddings(chunk)
    if chunk_emb_result is None:
        return 0, None

    chunk_embedding = chunk_emb_result[0]
    best_score = 0
    best_source = "local_database"
    best_url = None
    best_title = "Local Reference Database"

    if ref_embeddings and ref_embeddings[0] is not None:
        for ref_emb in ref_embeddings:
            similarity = cosine_similarity(chunk_embedding, ref_emb)
            if similarity > best_score:
                best_score = similarity

    try:
        web_refs = get_web_references(chunk, max_results=3)
        for web_ref in web_refs:
            web_text = web_ref["text"]
            web_sentences = [s.strip() for s in web_text.split('.') if len(s.strip()) > 15][:15]
            if web_sentences:
                web_embeddings = get_embeddings(web_sentences)
                if web_embeddings:
                    for web_emb in web_embeddings:
                        similarity = cosine_similarity(chunk_embedding, web_emb)
                        if similarity > best_score:
                            best_score = similarity
                            best_source = "web"
                            best_url = web_ref["url"]
                            best_title = web_ref["title"]
    except Exception as e:
        print(f"  [Warn] Web search failed for this chunk: {e}")

    flagged = None
    if best_score > 0.5:
        flagged = {
            "text": chunk,
            "type": "paraphrased",
            "confidence": round(best_score, 2),
            "source": best_source,
            "source_url": best_url,
            "source_title": best_title
        }
    return best_score, flagged


def detect_plagiarism_with_web(input_text):
    """
    Enhanced detection that searches the live internet concurrently.
    Uses chunking and ThreadPoolExecutor for speed.
    """
    raw_sentences = [s.strip() for s in input_text.split('.') if s.strip()]
    raw_sentences = [s for s in raw_sentences if len(s) >= 10]

    # Chunking: Group every 2 sentences to halve the API requests
    chunks = []
    for i in range(0, len(raw_sentences), 2):
        chunk = ". ".join(raw_sentences[i:i+2])
        chunks.append(chunk)

    if not chunks:
        return {"overall_score": 0, "ai_generated_score": 0, "paraphrased_score": 0, "ai_detection_details": {}, "status": "done", "flagged_sections": []}

    flagged_sections = []
    total_score = 0

    ref_embeddings = get_embeddings(REFERENCE_TEXTS)
    if ref_embeddings is None:
        ref_embeddings = [None] * len(REFERENCE_TEXTS)

    # Use ThreadPoolExecutor for concurrent searching
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(_process_chunk, chunk, ref_embeddings): chunk for chunk in chunks}
        
        for future in as_completed(futures):
            chunk = futures[future]
            try:
                score, flagged = future.result()
                total_score += score
                
                if flagged:
                    flagged["start"] = input_text.find(chunk)
                    flagged["end"] = input_text.find(chunk) + len(chunk)
                    flagged_sections.append(flagged)
            except Exception as e:
                print(f"[Warn] Thread error on chunk: {e}")

    overall_score = round((total_score / len(chunks)) * 100, 1) if chunks else 0

    ai_result = detect_ai_content(input_text)
    ai_generated_score = ai_result["ai_probability"]

    return {
        "overall_score": overall_score,
        "ai_generated_score": ai_generated_score,
        "paraphrased_score": round(overall_score * 0.4, 1),
        "ai_detection_details": ai_result,
        "status": "done",
        "flagged_sections": flagged_sections
    }


# Test it directly
if __name__ == "__main__":
    test_text = "Artificial intelligence has revolutionised the way we process information. Plagiarism is copying someone else's work."
    print("--- Offline Detection ---")
    result = detect_plagiarism(test_text)
    print(result)
    print("\n--- Web-Enhanced Detection ---")
    result = detect_plagiarism_with_web(test_text)
    print(result)