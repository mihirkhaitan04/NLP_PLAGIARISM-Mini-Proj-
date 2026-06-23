from sentence_transformers import SentenceTransformer, util

# Load the AI model (downloads once, then uses local copy)
model = SentenceTransformer('all-MiniLM-L6-v2')

# This is your reference database - texts to compare against
REFERENCE_TEXTS = [
    "Artificial intelligence has revolutionised the way we process information in modern systems.",
    "Machine learning models are trained on large datasets to make predictions.",
    "Plagiarism is the act of using someone else's work without giving proper credit.",
    "Deep learning uses neural networks with many layers to learn complex patterns.",
    "Natural language processing helps computers understand and generate human language.",
]

def detect_plagiarism(input_text):
    # Split input into sentences
    sentences = [s.strip() for s in input_text.split('.') if s.strip()]
    
    flagged_sections = []
    total_score = 0

    for sentence in sentences:
        # Get AI embedding for this sentence
        sentence_embedding = model.encode(sentence, convert_to_tensor=True)
        
        # Compare against all reference texts
        best_score = 0
        for ref in REFERENCE_TEXTS:
            ref_embedding = model.encode(ref, convert_to_tensor=True)
            similarity = util.cos_sim(sentence_embedding, ref_embedding).item()
            if similarity > best_score:
                best_score = similarity

        total_score += best_score

        # If similarity is high enough, flag it
        if best_score > 0.5:
            flagged_sections.append({
                "start": input_text.find(sentence),
                "end": input_text.find(sentence) + len(sentence),
                "text": sentence,
                "type": "paraphrased",
                "confidence": round(best_score, 2)
            })

    # Calculate overall score as percentage
    overall_score = round((total_score / len(sentences)) * 100, 1) if sentences else 0

    return {
        "overall_score": overall_score,
        "ai_generated_score": round(overall_score * 0.6, 1),
        "paraphrased_score": round(overall_score * 0.4, 1),
        "status": "done",
        "flagged_sections": flagged_sections
    }


# Test it directly
if __name__ == "__main__":
    test_text = "Artificial intelligence has revolutionised the way we process information. Plagiarism is copying someone else's work."
    result = detect_plagiarism(test_text)
    print(result)