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
The core of the detection engine utilizes the `all-MiniLM-L6-v2` model from the `SentenceTransformers` library. 

### Why MiniLM?
While larger models (like BERT-base or RoBERTa) offer marginally higher accuracy, `MiniLM` strikes an elite balance between computational efficiency and semantic density. It projects sentences into a 384-dimensional dense vector space. 

### The Mathematics of Detection
1. **Tokenization & Pooling:** Raw text is tokenized, passed through the transformer layers, and mean-pooled to generate a single dense vector representation of the sentence.
2. **Cosine Similarity:** The system computes the cosine of the angle between the input vector ($\vec{A}$) and reference vectors ($\vec{B}$). 
   $$ \text{Similarity} = \cos(\theta) = \frac{\vec{A} \cdot \vec{B}}{\|\vec{A}\| \|\vec{B}\|} $$
3. **Thresholding:** A dynamic confidence threshold (currently $\tau > 0.5$) is applied. If the spatial distance between the input vector and a known source vector crosses this threshold, it is flagged. Because the comparison is geometric rather than alphabetical, synonym swapping does not fool the detector.

## 4. Performance Considerations
* **Memory Management:** PyMuPDF (`fitz`) is utilized for PDF extraction due to its C-level bindings, making it significantly faster and more memory-efficient than pure-Python alternatives like `PyPDF2`.
* **Stateless Processing:** The API routes are stateless. The AI model is loaded into memory exactly once at application startup (singleton pattern) to eliminate cold-start latency during inference requests.

## 5. Strategic Roadmap & Scalability
To transition this architecture to handle enterprise-level traffic, the following upgrades are conceptually mapped:
1. **Distributed Task Queues:** Implementing **Celery** with a **Redis** broker. When a user uploads a 500-page manuscript, the HTTP request should return a `202 Accepted` immediately, delegating the vector inference to background worker nodes.
2. **Vector Databases (faiss / Pinecone):** As the reference database grows from a few sentences to millions of articles, $O(N)$ linear scanning becomes a bottleneck. Integrating a dedicated vector database utilizing Approximate Nearest Neighbor (ANN) algorithms (like HNSW) will reduce search times from seconds to milliseconds.
3. **Live Web Scraping:** Integrating a web-crawling heuristic to dynamically pull top Google Search results for the inputted text, converting the live internet into the reference database in real-time.
