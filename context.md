# Project Context & Architectural Decisions (ADR)

## 1. Executive Summary
The **NLP Plagiarism Detector** is designed not simply as a text-matching script, but as a scalable, high-throughput document analysis pipeline. Traditional plagiarism detectors rely heavily on lexical matching (n-grams, Jaccard similarity, or exact substring matching). These legacy systems fail catastrophically when faced with modern "smart" plagiarism—such as heavy paraphrasing, synonym replacement, or content rewritten by generative AI. 

To solve this, this system shifts the paradigm from **Lexical Matching** to **Semantic Vectorization**. By embedding text into high-dimensional vector spaces, the engine can measure the *mathematical distance in meaning* between two sentences, effectively catching advanced obfuscation techniques.

## 2. System Architecture
The application adopts a decoupled, service-oriented architecture to separate heavy mathematical computation from high-speed I/O routing.

* **Client Layer (React + Vite):** A lightweight, component-driven SPA (Single Page Application). Vite was chosen over Webpack for its native ES-module hot-module replacement (HMR), reducing build times to milliseconds. Tailwind CSS ensures zero-runtime styling overhead.
* **API Gateway & Routing (FastAPI):** FastAPI serves as the central orchestrator. Built on Starlette and Pydantic, it provides an ASGI (Asynchronous Server Gateway Interface) foundation. This is critical for handling concurrent I/O bottlenecks—such as reading multi-megabyte PDF streams into memory—without blocking the main thread.
* **Database Persistence (PostgreSQL):** PostgreSQL was selected for its robust ACID compliance and superior JSONB support, allowing dynamic, unstructured AI analysis results to be queried efficiently alongside structured metadata (timestamps, UUIDs).
* **AI Inference Engine (Flask / SentenceTransformers):** The NLP logic is isolated to prevent its heavy CPU/GPU memory footprint from interfering with the API layer's responsiveness.

## 3. The Algorithmic Core: Semantic Embeddings
The core of the detection engine utilizes the `paraphrase-multilingual-MiniLM-L12-v2` model from the `SentenceTransformers` library. This multilingual model supports 50+ languages, enabling cross-lingual plagiarism detection.

### Why Multilingual MiniLM?
While larger models (like BERT-base or RoBERTa) offer marginally higher accuracy, the multilingual `MiniLM` strikes an elite balance between computational efficiency and semantic density. It projects sentences from any of 50+ languages into a shared 384-dimensional dense vector space, meaning a sentence in Spanish and its English translation will have nearly identical vectors.

### AI-Generated Content Detection
In addition to plagiarism detection, the system incorporates a secondary GPT-2-based perplexity analyzer (`ai_detector.py`). This module measures how "predictable" the submitted text is to a language model. AI-generated text tends to have significantly lower perplexity than human writing. This is combined with a burstiness metric (variation in sentence lengths) to produce a composite AI probability score.
### The Mathematics of Detection
1. **Tokenization & Pooling:** Raw text is tokenized, passed through the transformer layers, and mean-pooled to generate a single dense vector representation of the sentence.
2. **Cosine Similarity:** The system computes the cosine of the angle between the input vector ($\vec{A}$) and reference vectors ($\vec{B}$). 
   $$ \text{Similarity} = \cos(\theta) = \frac{\vec{A} \cdot \vec{B}}{\|\vec{A}\| \|\vec{B}\|} $$
3. **Thresholding:** A dynamic confidence threshold (currently $\tau > 0.5$) is applied. If the spatial distance between the input vector and a known source vector crosses this threshold, it is flagged. Because the comparison is geometric rather than alphabetical, synonym swapping does not fool the detector.

## 4. Performance Considerations
* **Memory Management:** PyMuPDF (`fitz`) is utilized for PDF extraction due to its C-level bindings, making it significantly faster and more memory-efficient than pure-Python alternatives like `PyPDF2`.
* **Stateless Processing:** The API routes are stateless. The AI model is loaded into memory exactly once at application startup (singleton pattern) to eliminate cold-start latency during inference requests.

## 5. Strategic Roadmap & Future Enhancements
To transition this architecture to handle enterprise-level traffic and provide a world-class user experience, the following upgrades are conceptually mapped into our roadmap:

### 5.1 AI & NLP Enhancements (IMPLEMENTED)
* **Live Internet Scraping:** [DONE] Transitioned from a static reference database to a dynamic web-crawling heuristic using the DuckDuckGo API. The engine scrapes live content and compares vector embeddings against the public internet in real-time.
* **AI-Generated Content Detection:** [DONE] Integrated a GPT-2 perplexity analyzer combined with burstiness scoring to calculate the probabilistic likelihood that submitted text was authored by an LLM (ChatGPT/Claude) versus a human.
* **Multi-Language Support:** [DONE] Upgraded the SentenceTransformer to `paraphrase-multilingual-MiniLM-L12-v2`, a cross-lingual embedding model supporting 50+ languages. Detects translated plagiarism across language boundaries.

### 5.2 Frontend & User Experience
* **Side-by-Side Diff Viewer:** Implementing a GitHub-style split-screen interface using React. This will display the user's uploaded text alongside the source material, visually highlighting the exact overlapping vectors in red.
* **Downloadable PDF Reports:** Allowing users to export comprehensive, mathematically-backed plagiarism reports (including confidence charts and flagged text) directly from the React frontend.
* **Dynamic Data Visualization:** Utilizing libraries like `Recharts` to build an analytical dashboard, featuring radial progress bars for "Originality Score" and radar charts breaking down textual metrics.

### 5.3 Architecture & Infrastructure
* **One-Click Dockerization:** Containerizing the entire stack (Frontend, FastAPI Backend, NLP Engine, and PostgreSQL) via `docker-compose`. This ensures environment parity and allows the entire microservices architecture to be spun up with a single command.
* **User Authentication:** Implementing JWT-based stateless authentication. This enables multi-tenant capabilities where users can maintain private dashboards and historical submission records safely.
* **Asynchronous Task Queue:** Implementing **Celery** with a **Redis** broker. When a user uploads a massive document, the HTTP request returns a `202 Accepted` immediately, delegating the heavy vector inference to background worker nodes while pushing real-time progress updates to the frontend via WebSockets.
