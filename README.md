# CFO Buddy 💼

An intelligent financial assistant powered by LangGraph, LLM, and HuggingFace. 
---

## Project Structure

```
cfobuddy/
├── app.py                  ← entry point
├── build_index.py           ← run once to index your data
├── requirements.txt
├── .env
├── .gitignore
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
│   ├── search.py            ← search_financial_docs (FAISS)
│   ├── lookup.py            ← exact_lookup, list_available_files
│   └── web_search.py        ← brave_search
│
├── data/                    ← put your files here
│   ├── FinancialStatements.csv
│   ├── cards_data.csv
│   └── report.pdf
│
└── faiss_index/             ← auto-generated, do not commit
```

## Features

- **Multi-file support** — CSV, PDF, Excel, Word
- **Semantic search** — find relevant data across all your documents
- **Exact lookup** — precise queries by ID, account number, card number etc.
- **Web search** — live market data and news via Brave Search
- **Persistent memory** — conversations saved to SQLite, resumable by thread ID
- **LangGraph architecture** — modular, extensible graph-based agent

---

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
GROQ_API_KEY=your_groq_api_key
BRAVE_SEARCH_API_KEY=your_brave_api_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=CFOBuddy
```

Get your API keys:
- **Groq** (free): [console.groq.com](https://console.groq.com)
- **Brave Search** (free, 2000 req/month): [brave.com/search/api](https://brave.com/search/api)
- **LangSmith** (optional, for tracing): [smith.langchain.com](https://smith.langchain.com)

### 5. Add your data files

Drop your files into the `data/` folder. Supported formats:

| Format | Extension |
|--------|-----------|
| CSV | `.csv` |
| PDF | `.pdf` |
| Excel | `.xlsx`, `.xls` |
| Word | `.docx` |

### 6. Build the FAISS index

Run this **once** (or whenever you add/change files in `data/`):

```bash
python build_index.py
```

### 7. Run CFO Buddy

```bash
python main.py
```

---

## Usage

```
==================================================
  CFO Buddy — Ready!
  Type 'exit' to quit.
  Type 'threads' to see past conversations.
==================================================

Thread ID (press Enter for 'main'): 
Using thread: main

```

### Resume a previous conversation

Each conversation is saved by `thread_id`. To resume:

```
Thread ID (press Enter for 'main'): analysis_q3
```

---

## Agent Architecture

```
[START]
   │
   ▼
[upload_node]     ← placeholder for future file upload feature
   │
   ▼
[model]           ← Groq LLM decides what to do
   │
   ├── tool call? ──► [tools] ──► back to [model]
   │
   └── no tool ──► [END]
```

## Tools

| Tool | Description |
|------|-------------|
| `search_financial_docs` | Semantic search across all indexed files |
| `exact_lookup` | Exact match by column value in CSV files |
| `list_available_files` | Lists all files and CSV columns |
| `brave_search` | Live web search via Brave API |

