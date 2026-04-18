# CFO Buddy 💼

An intelligent financial assistant powered by LangGraph, LLM, and HuggingFace. 
---

## Project Structure

```
cfobuddy/
├── main.py                  ← entry point
├── build_index.py           ← run once to index your data
├── requirements.txt
├── .env
├── .gitignore
│
├── api/
│   ├── __init__.py
│   └── app.py               ← FastAPI server
│
├── core/
│   ├── __init__.py
│   ├── graph.py             ← StateGraph, nodes, edges
│   ├── state.py             ← State TypedDict
│   ├── llm.py               ← Groq LLM setup
│   ├── embeddings.py        ← HuggingFace embeddings
│   └── memory.py            ← SqliteSaver + thread management
│
├── tools/
│   ├── __init__.py
│   ├── search.py            ← LlamaIndex + Neon pgvector search
│   ├── lookup.py            ← exact_lookup, list_available_files
│   ├── finance_api.py       ← yfinance + Twelve Data
│   ├── chart.py             ← chart generation tool
│   └── web_search.py        ← DuckDuckGo search
│
└── data/                    ← put your files here (not committed)
    ├── FinancialStatements.csv
    └── report.pdf
```

---

## Features

- **Multi-file support** — CSV, PDF, Excel, Word
- **Hybrid retrieval search** — Semantic (LlamaIndex + Neon pgvector) + keyword BM25 (local docs in `data/`)
- **Exact lookup** — precise queries by ID, account number, card number etc.
- **Live financial data** — stock prices, income statements, balance sheets via yfinance + Twelve Data
- **Web search** — real-time news via DuckDuckGo
- **Chart generation** — auto-generates Plotly charts from financial data
- **Persistent memory** — conversations saved to SQLite by thread ID
- **LangGraph architecture** — modular, extensible graph-based ReAct agent
- **FastAPI** — production-ready REST API with auto-generated docs

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/caffeicsatyam/cfobuddy.git
cd cfobuddy
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the root:

```env
# LLM
GROQ_API_KEY=your_groq_api_key

# Vector DB
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require
NEON_HOST=your_neon_host
NEON_DATABASE=your_db_name
NEON_USER=your_user
NEON_PASSWORD=your_password

# Financial APIs
TWELVE_DATA_API_KEY=your_twelve_data_key

# Tracing (optional)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key
LANGSMITH_PROJECT=CFOBuddy
```

Get your API keys:
- **Groq** (free): [console.groq.com](https://console.groq.com)
- **Neon DB** (free): [neon.tech](https://neon.tech)
- **Twelve Data** (free, 800 req/day): [twelvedata.com](https://twelvedata.com)
- **LangSmith** (optional): [smith.langchain.com](https://smith.langchain.com)

### 5. Enable pgvector on Neon

In your Neon dashboard SQL editor run:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 6. Add your data files

Drop your files into the `data/` folder. Supported formats:

| Format | Extension |
|--------|-----------|
| CSV | `.csv` |
| PDF | `.pdf` |
| Excel | `.xlsx`, `.xls` |
| Word | `.docx` |

### 7. Build the index

Run this **once** (or whenever you add/change files in `data/`):

```bash
python build_index.py
```

### 8. Run CFO Buddy

**CLI:**
```bash
python app.py
```

**API:**
```bash
python main.py
```

---

## Usage

```
==================================================
  CFO Buddy — Ready!
  Type 'exit' or 'stop' to quit.
  Type 'threads' to see past conversations.
==================================================

Session ID: 3f7a1c2d-...

You: what was Zomato revenue in Q3FY25?
CFO Buddy: Consolidated Adjusted Revenue grew 58% YoY to INR 5,746 crore...

You: AAPL stock price
CFO Buddy: Apple Inc. (AAPL) — Price: $213.49 | Market Cap: $3.21T...

You: find card id 4524
CFO Buddy: Found 1 record in cards_data.csv...
```

---

## API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| `GET` | `/` | API info |
| `GET` | `/health` | Health check |
| `POST` | `/chat` | Send message |
| `GET` | `/threads` | List all threads |
| `GET` | `/files` | List data files |
| `POST` | `/upload` | Upload a file |

Auto-generated docs at **http://localhost:8000/docs**

---

## Agent Architecture

```text
[START]
   │
[upload_node] (future file upload handling)
   │
   └── route_after_upload (Fast Semantic Routing)
         ├── [model] ⟷ [internal_tools] ──► END
         │
         ├── [sql_node] ⟷ [sql_tools] ──► END
         │
         ├── [finance_node] ⟷ [finance_tools] ──► END
         │
         └── [web_search_node] ⟷ [web_search_tools] ──► END
```

---

## Tools

| Tool | Source | Description |
|------|--------|-------------|
| `search_financial_docs` | LlamaIndex + Neon + BM25 | Hybrid retrieval (semantic + keyword) across local files |
| `exact_lookup` | pandas | Exact match by column value in CSVs |
| `list_available_files` | local | Lists all files and CSV columns |
| `get_financial_data` | yfinance + Twelve Data | Live stock quotes, financials, news |
| `generate_chart` | Plotly | Auto-generates charts from data |
| `brave_search` | DuckDuckGo | Real-time web search |

---

## Hybrid retrieval settings

- `RAG_DATA_DIR` (default: `data`) — local folder used to build the BM25 corpus
- `RAG_TOP_K` (default: `5`) — number of chunks returned
- `HYBRID_ALPHA` (default: `0.6`) — weight for semantic/vector results
- `HYBRID_BETA` (default: `0.4`) — weight for BM25 keyword results

---

## Roadmap

- [x] Fast Semantic LLM Router
- [x] Multi-agent Graph Architecture (SQL, Finance, Web)
- [x] Next.js frontend integration
- [ ] Per-user vector stores for uploads
- [ ] Multi-user authentication

---

## License

MIT
