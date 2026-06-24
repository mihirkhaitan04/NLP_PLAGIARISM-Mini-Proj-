# 🚀 NEXT FEATURE: Forensic Stylometry Tribunal (LangGraph + Gemini)

We are building a Multi-Agent Debate using LangGraph, powered by the Gemini API, to perform deep Forensic Stylometric Analysis. 

## The Concept
Instead of a simple API call, we will create three separate AI Agents:
1. **The Prosecutor:** Argues why the new document's style does not match the user's past documents (Plagiarism/AI Generated!).
2. **The Defense:** Argues why the style similarities suggest the student is innocent.
3. **The Judge:** Weighs both and provides a final "Author Match Score".

## Step-by-Step Implementation Plan

### 1. Dependencies
- **Action:** Run `pip install langchain langgraph langchain-google-genai`
- **Action:** Add these to `plagiarism-backend/requirements.txt`
- **Action:** Add `GEMINI_API_KEY=your_key_here` to `plagiarism-backend/.env`

### 2. Backend Modifications
- **`db.py`**: Add a `get_recent_texts(limit=3)` function to pull historical documents for fingerprinting.
- **`tribunal.py`**: Create this new file to build the LangGraph workflow with the three nodes (Prosecutor, Defense, Judge).
- **`worker.py`**: Update the Celery worker to run the `tribunal.py` workflow alongside the regular scan, and save the Tribunal's JSON output to Postgres.

### 3. Frontend Modifications
- **`Results.jsx`**: Add a new UI panel to display the "AI Tribunal". It should visually show the Prosecutor's argument (Red), the Defense's argument (Blue), and the Judge's Final Verdict (Gold).
