# NEXUS — Evidence Intelligence for AI

[![CI/CD Pipeline](https://github.com/Kushal026/NEXUS-RAG/actions/workflows/ci.yml/badge.svg)](https://github.com/Kushal026/NEXUS-RAG/actions)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14.2.1-black?logo=next.js)](https://nextjs.org)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?logo=docker)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**NEXUS** is an enterprise-grade, state-of-the-art **Evidence Intelligence & Neural Retrieval Platform**. It moves beyond naive chunk-level Retrieval-Augmented Generation by unifying **Hybrid Sparse-Dense Search (MiniLM + BM25 RRF)**, **Cross-Encoder Reranking**, **Neo4j Knowledge Graph Traversal**, **Temporal Filtering & Conflict Resolution**, **NLI Contradiction Analysis**, **Iterative Self-Correcting Recovery**, **Multimodal Document Understanding (PDF, Tables, Charts, Images/OCR, Code)**, and an **Autonomous 9-Section Research Agent**.

> **Tagline**: *Retrieve, connect, verify, and reason over complex information with evidence-backed AI.*

---

## 🌟 Architecture & Interactive Pipeline

```
                                  +---------------------------------------+
                                  |         NEXUS Research Agent          |
                                  |   (Planner, Gap Detector, Synthesizer)|
                                  +---------------------------------------+
                                                     |
  +-----------------------+                          v                          +-----------------------+
  |  Multimodal Ingestion | ----> [ Hybrid Sparse-Dense Search (RRF) ] <---- |  Knowledge Graph RAG  |
  |  - PDF / Text / Code  |       [   MiniLM-L6-v2 + BM25 Indexing   ]       |  - Neo4j / In-Memory  |
  |  - Tables (CSV/HTML)  |                          |                          |  - Entity Resolution  |
  |  - Charts & Figures   |                          v                          |  - Path Traversal     |
  |  - Images (OCR Vision)|              [ Cross-Encoder Reranker ]             +-----------------------+
  +-----------------------+                          |
                                                     v
                                  +---------------------------------------+
                                  |     Evidence Intelligence Engine      |
                                  |  - Pairwise NLI Contradiction Analysis|
                                  |  - Temporal Conflict Resolution       |
                                  |  - Source Reliability Scoring         |
                                  +---------------------------------------+
                                                     |
                                                     v
                                  +---------------------------------------+
                                  |     Self-Correcting Retrieval Loop    |
                                  |  - Retrieval Quality Evaluator        |
                                  |  - Targeted Query Rewriter            |
                                  |  - Answer Verifier (Zero-Hallucination|
                                  +---------------------------------------+
```

### 8-Stage Deterministic Verification Pipeline
1. **UNDERSTAND**: Decompose complex questions into atomic sub-aspects, temporal filters, and entity anchors.
2. **RETRIEVE**: Simultaneously query 384-dimensional dense semantic vectors and lexical BM25 token indices.
3. **RERANK**: Compute exact cross-attention relevance scores for top candidate pools via `ms-marco-MiniLM-L-6-v2`.
4. **CONNECT**: Expand retrieved facts with 2-hop entity relations, typed links, and document citations.
5. **COMPARE**: Perform pairwise NLI entailment checks to detect conflicting claims across disparate sources.
6. **VERIFY**: Confirm that accumulated evidence answers all sub-inquiries before generating conclusions.
7. **REASON**: Synthesize structured findings with strict boundary isolation against prompt injection.
8. **CITE**: Attribute every single claim to exact document names, pages, and verifiable quotes.

---

## 🚀 Key Platform Features

### 1. Public Landing Page & Experience
- **Interactive Pipeline Visualizer**: Live animated representation of document extraction, dual-index retrieval, evidence verification, and citation synthesis.
- **8 Capabilities Bento Grid**: Interactive cards for all intelligence subsystems.
- **Evidence Transparency Breakdown**: Demonstrates claim-level citations, contradiction detection, and prompt defense.

### 2. Authentication & Multi-User Data Isolation
- **Secure JWT Session Management**: Cryptographic HMAC SHA-256 password hashing and signed JWT tokens with 24-hour expiration.
- **Multiple Auth Providers**: Email/Username registration & login, password recovery with 30-minute tokens, and "Continue with Google".
- **User Profile Management**: Global user profile dropdown with avatar initials, role badge, and session controls.
- **Multi-Tenant Data Isolation**: Private document vaults and user-scoped vector retrievals preventing unauthorized data access.

### 3. Hybrid Sparse-Dense Retrieval & Cross-Encoder Reranking
- **Dense Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` with Cosine Similarity indexing.
- **Sparse Keyword Search**: BM25 ranking algorithm with term-frequency token normalization.
- **Reciprocal Rank Fusion (RRF)**: $RRF(d) = \sum_{m} \frac{1}{k + r_m(d)}$ where $k=60$.
- **Neural Cross-Encoder**: `cross-encoder/ms-marco-MiniLM-L-6-v2` calculating deep query-document relevance logits.

### 4. Knowledge Graph Intelligence (Neo4j & In-Memory)
- Multi-layer entity extraction across 12 domain taxonomies (`Person`, `Organization`, `Model`, `Technology`, `Dataset`, `Concept`, `Paper`, `Date`).
- Relationship extraction (`AUTHORED_BY`, `USES`, `DEPENDS_ON`, `INTRODUCED`, `COMPETES_WITH`, `EVALUATED_ON`).
- Entity resolution with Jaro-Winkler string similarity and provenance tracking.
- Multi-hop graph traversal and Cypher neighborhood expansion.

### 5. Evidence Intelligence & NLI Contradiction Detection
- Pairwise natural language inference: classifies relationships as **Agreement**, **Direct Contradiction**, **Partial Contradiction**, **Different Conditions**, or **Temporal Difference**.
- Transparent multi-factor source reliability scoring: Authority, Venue Type, Corroboration Factor, Temporal Decay.
- Strict `⚠ Conflicting evidence` warnings with contextual discrepancy explanations.

### 6. Self-Correcting Iterative Retrieval Engine
- Automated retrieval quality evaluation across Relevance, Evidence Coverage, Source Quality, Redundancy, and Temporal Suitability.
- Targeted query rewriting to fill identified missing evidence gaps.
- Multi-iteration evidence accumulation preventing data loss.
- Post-generation zero-hallucination factual claim verification.

### 7. Multimodal Evidence Engine
- Complete document hierarchy representation: `Document -> Text, Tables, Figures, Images, Metadata, References`.
- Specialized parsers for Markdown/CSV/HTML tables, chart axes/visible values, OCR images, and 15+ programming languages.
- Strict citation provenance tracking (e.g. `Figure 3 • Paper.pdf • Page 12`).

### 8. NEXUS Autonomous Research Agent
- Autonomous bounded research planner decomposing goals into analytical sub-questions.
- Multi-hop iterative evidence reading, gap detection, and graph-guided exploration.
- Generates structured 9-section academic research reports with interactive source tables.
- Strict budget guards (`max_iterations`, `max_searches`, `max_time_seconds`) and high-level action tracing.

### 9. Production Engineering, Security & Observability
- **Prompt Injection Defense**: `<untrusted_document_context>` XML boundary tags, immutable system prompts, delimiter sanitization.
- **SSRF Guard**: Prohibits private networks (`10.0.0.0/8`, `192.168.0.0/16`, `127.0.0.1`, cloud metadata `169.254.169.254`).
- **Global Command Palette**: Instant navigation and research execution via `⌘K` / `Ctrl+K`.
- **Theme**: High-end clean light interface with accessibility and WCAG AA contrast.
- **Observability**: Prometheus `/metrics`, `/health`, `/readiness`, and structured logging.

---

## 🛠 Quickstart Guide

### Prerequisites
- Python 3.11+
- Node.js 18+ (for frontend)
- Docker & Docker Compose (optional for containerized deployment)

### 1. Local Python & Next.js Setup

```bash
# Clone repository
git clone https://github.com/Kushal026/NEXUS-RAG.git
cd NEXUS-RAG

# Backend Setup
cd backend
python -m venv venv
# Activate virtual environment (Windows: venv\Scripts\activate, Linux/macOS: source venv/bin/activate)
pip install -r requirements.txt

# Start Backend API Server (Port 8000)
uvicorn app.main:app --reload --port 8000

# Frontend Setup (in separate terminal)
cd ../frontend
npm install
npm run dev
# Frontend will be live at http://localhost:3000
```

### 2. Default Test Credentials
- **Admin**: `admin` / `AdminSecure2026!`
- **Researcher**: `researcher` / `Researcher2026!`

---

## 🧪 Testing & Validation

Run the complete 97-test validation suite:

```bash
python -m pytest backend/tests/ -v
```

---

## 📄 License
This project is licensed under the MIT License.