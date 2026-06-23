# ⚡ NLP Plagiarism Detector & Document Analyzer ⚡

Hello there! 👋

I am excited to share my NLP Plagiarism Detector project, which analyzes documents using advanced Natural Language Processing to detect copied content and paraphrasing. 

But it doesn't stop at simple text matching. This project is a complete, end-to-end full-stack application that incorporates modern frontend design (React + Tailwind), high-performance API routing (FastAPI), and state-of-the-art AI embeddings (SentenceTransformers).

Think of it as: A sophisticated document analysis suite with an AI-powered detection engine, persistent database storage, and a sleek user interface.

## ✨ Key Features
This tool is designed to automate the process of analyzing text and PDFs for plagiarism. Key features include:

**1. Advanced AI Detection (Pillar 1)**
* **Live Internet Scraping:** Dynamically searches the web via DuckDuckGo and scrapes live articles to cross-reference against the entire public internet, not just a static database.
* **Semantic Matching:** Uses the `all-MiniLM-L6-v2` Sentence Transformer model to understand the *meaning* of text, not just exact word matches.
* **Paraphrase Detection:** Effectively catches content that has been rewritten or reworded to hide plagiarism.
* **Confidence Scoring:** Provides percentage scores indicating the likelihood of plagiarized and paraphrased content.

**2. High-Performance Backend (Pillar 2)**
* **FastAPI Architecture:** Ensures lightning-fast API responses and efficient handling of asynchronous requests.
* **PDF Parsing:** Built-in support for extracting raw text directly from PDF documents using PyMuPDF.
* **PostgreSQL Integration:** Securely stores submission history, raw text, and detailed analysis results for future review.

**3. Modern Frontend Dashboard (Pillar 3)**
* **React & Vite:** A lightning-fast, component-based user interface for seamless interaction.
* **Scan Modes:** Allows users to easily toggle between a "Deep Web Scan" and a "Fast Local Scan".
* **Source Attribution:** Dynamically renders clickable links directly to the plagiarized source website.
* **Tailwind CSS:** Beautiful, responsive design with support for modern UI paradigms.

---

## 🛠️ Usage
Here’s how to get started with the NLP Plagiarism Detector. 👇

**Step 1: Setup the Database**
Ensure you have PostgreSQL installed and running. Create a `.env` file in the `plagiarism-backend` directory with your database credentials:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=plagiarism_db
DB_USER=postgres
DB_PASSWORD=yourpassword
```

**Step 2: Start the Backend API & NLP Engine**
Navigate to the backend directory, install the Python dependencies, and start the FastAPI server.
```bash
cd plagiarism-backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
*(Note: The system will automatically download the SentenceTransformer AI model upon its first run).*

**Step 3: Start the Frontend Dashboard**
Navigate to the frontend directory, install the Node packages, and start the Vite development server.
```bash
cd plagiarism-frontend
npm install
npm run dev
```
Open the provided local URL (e.g., `http://localhost:5173`) in your web browser to view the live dashboard and start analyzing documents!

---

## 📁 Project Structure
Here’s how the project is organized for maximum clarity and separation of concerns:

* **`plagiarism-frontend/`**: The React-based user interface. Contains components for file uploads, score display, and submission history.
* **`plagiarism-backend/`**: The FastAPI server. Handles PDF extraction, API endpoints (`main.py`), and PostgreSQL database interactions (`db.py`).
* **`plagiarism-nlp/`**: The core AI engine. Contains `detect.py` which houses the SentenceTransformer logic and reference database.

---

## 🤔 Why This Architecture?
This tool provides a robust, scalable solution for document analysis. Key benefits include:

* **Modular Design:** The clear separation between the UI, the API router, and the AI engine means any component can be scaled or upgraded independently.
* **Intelligent Analysis:** By utilizing vector embeddings rather than simple string matching, the system catches nuanced paraphrasing that traditional tools completely miss.

Feel free to hit me up with new ideas or queries regarding my project!
