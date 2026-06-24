from sentence_transformers import SentenceTransformer, util
from web_scraper import get_web_references
from ai_detector import detect_ai_content

# Load the multilingual AI model (supports 50+ languages including Hindi, Spanish, French, etc.)
# This replaces the English-only 'all-MiniLM-L6-v2' with a cross-lingual model
print("[Info] Loading multilingual SentenceTransformer model...")
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
print("[Info] Multilingual model loaded successfully.")

# This is your local reference database - texts to compare against (offline fallback)
REFERENCE_TEXTS = [
    "Artificial intelligence has revolutionised the way we process information in modern systems.",
    "Machine learning models are trained on large datasets to make predictions.",
    "Plagiarism is the act of using someone else's work without giving proper credit.",
    "Deep learning uses neural networks with many layers to learn complex patterns.",
    "Natural language processing helps computers understand and generate human language.",
]


def detect_plagiarism(input_text):
    """Original offline-only detection (kept as fallback)."""
    sentences = [s.strip() for s in input_text.split('.') if s.strip()]

    flagged_sections = []
    total_score = 0

    for sentence in sentences:
        sentence_embedding = model.encode(sentence, convert_to_tensor=True)

        best_score = 0
        for ref in REFERENCE_TEXTS:
            ref_embedding = model.encode(ref, convert_to_tensor=True)
            similarity = util.cos_sim(sentence_embedding, ref_embedding).item()
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


def detect_plagiarism_with_web(input_text):
    """
    Enhanced detection that searches the live internet for each sentence.
    Combines web-scraped references with the local reference database.
    Uses multilingual model for cross-language plagiarism detection.
    """
    sentences = [s.strip() for s in input_text.split('.') if s.strip()]

    flagged_sections = []
    total_score = 0

    for sentence in sentences:
        if len(sentence) < 10:
            continue

        print(f"  [Search] Searching web for: \"{sentence[:60]}...\"")
        sentence_embedding = model.encode(sentence, convert_to_tensor=True)

        best_score = 0
        best_source = "local_database"
        best_url = None
        best_title = "Local Reference Database"

        # --- Phase 1: Compare against local reference database ---
        for ref in REFERENCE_TEXTS:
            ref_embedding = model.encode(ref, convert_to_tensor=True)
            similarity = util.cos_sim(sentence_embedding, ref_embedding).item()
            if similarity > best_score:
                best_score = similarity

        # --- Phase 2: Compare against live web results ---
        try:
            web_refs = get_web_references(sentence, max_results=3)
            for web_ref in web_refs:
                # Split the scraped web text into chunks for comparison
                web_text = web_ref["text"]
                web_sentences = [s.strip() for s in web_text.split('.') if len(s.strip()) > 15]

                for web_sentence in web_sentences[:20]:
                    web_embedding = model.encode(web_sentence, convert_to_tensor=True)
                    similarity = util.cos_sim(sentence_embedding, web_embedding).item()

                    if similarity > best_score:
                        best_score = similarity
                        best_source = "web"
                        best_url = web_ref["url"]
                        best_title = web_ref["title"]
        except Exception as e:
            print(f"  [Warn] Web search failed for this sentence, using local only: {e}")

        total_score += best_score

        # If similarity is high enough, flag it
        if best_score > 0.5:
            flagged_sections.append({
                "start": input_text.find(sentence),
                "end": input_text.find(sentence) + len(sentence),
                "text": sentence,
                "type": "paraphrased",
                "confidence": round(best_score, 2),
                "source": best_source,
                "source_url": best_url,
                "source_title": best_title
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


# Test it directly
if __name__ == "__main__":
    test_text = "Artificial intelligence has revolutionised the way we process information. Plagiarism is copying someone else's work."
    print("--- Offline Detection ---")
    result = detect_plagiarism(test_text)
    print(result)
    print("\n--- Web-Enhanced Detection ---")
    result = detect_plagiarism_with_web(test_text)
    print(result)