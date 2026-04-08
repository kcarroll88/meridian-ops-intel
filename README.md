<img width="1864" height="1239" alt="Screenshot 2026-04-06 at 12 55 33 PM" src="https://github.com/user-attachments/assets/4379262b-d1c4-4091-b81b-6ceabd512dd1" />



# Meridian Analytics Intelligence Assistant

An AI-powered research assistant that combines semantic search over internal documents with live web intelligence. Built on the **ReAct (Reasoning + Acting)** agent pattern, it routes natural language queries to the right data source automatically — internal knowledge base or real-time web search — and synthesizes a grounded answer with source attribution.

---

## Features

- **Dual-source retrieval** — searches internal PDFs and the live web in a single query
- **ReAct agent loop** — explicit thought/action/observation reasoning before every response
- **Visual reasoning trace** — see exactly which tools were used and why
- **Semantic search** — Voyage AI embeddings + ChromaDB for document retrieval
- **Persistent vector store** — documents are indexed once; ChromaDB persists across runs
- **Streamlit web UI** — glassmorphism chat interface with session history

---

## Architecture

```
User Query
    ↓
Streamlit Chat Interface (app.py)
    ↓
ReAct Agent — Claude Haiku (agent.py)
    ├── Knowledge Base Tool
    │     ├── Voyage-3 embedding of query
    │     └── Semantic search over ChromaDB (top 3 chunks)
    └── Web Search Tool
          └── Tavily API (up to 3 results)
    ↓
Synthesized answer with sources
```

**Document indexing pipeline:**

```
docs/*.pdf → PyPDFLoader → RecursiveCharacterTextSplitter
    → Voyage-3 Embeddings → ChromaDB collection
```

---

## Project Structure

```
ReAct-Agent/
├── agent.py          # Core agent logic, tool definitions, document indexing
├── app.py            # Streamlit UI (primary interface)
├── requirements.txt  # Python dependencies
├── .env              # API keys (not committed)
├── docs/             # Source PDFs for the knowledge base
└── chroma_db/        # Persistent vector store (auto-generated on first run)
```

---

## Setup

### Prerequisites

- Python 3.11+
- API keys for [Anthropic](https://console.anthropic.com), [Voyage AI](https://www.voyageai.com), and [Tavily](https://tavily.com)

### Installation

```bash
# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables
cp .env.example .env  # or create .env manually
```

Add your API keys to `.env`:

```env
ANTHROPIC_API_KEY=sk-ant-...
VOYAGE_API_KEY=pa-...
TAVILY_API_KEY=tvly-...
```

### Add Documents

Place PDF files in the `docs/` directory. They will be automatically indexed on first run.

---

## Usage

**Web UI (recommended):**

```bash
streamlit run app.py
```

**Standalone agent (test queries):**

```bash
python agent.py
```

---

## How It Works

The agent follows the ReAct loop on every query:

1. **Thought** — reasons about what type of question is being asked
2. **Action** — selects `KnowledgeBase` (internal docs) or `WebSearch` (live data)
3. **Observation** — receives tool output
4. Repeats up to 5 iterations, then produces a **Final Answer**

The Streamlit UI surfaces each step so you can follow the agent's reasoning in real time.

---

## Tech Stack

| Component | Library |
|-----------|---------|
| LLM | Claude Haiku (`claude-haiku-4-5-20251001`) |
| Agent framework | LangChain / LangGraph |
| Embeddings | Voyage AI (`voyage-3`) |
| Vector store | ChromaDB |
| Web search | Tavily |
| UI | Streamlit |
| PDF loading | PyPDF / LangChain document loaders |
