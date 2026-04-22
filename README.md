# CFO Buddy 💼

An intelligent, ChatGPT-inspired financial assistant powered by **LangGraph**, **FastAPI**, and **Next.js**. CFO Buddy helps you analyze financial statements, track stock trends, and generate insights from your data with a premium, human-like interface.

---

## ✨ Features

- **ChatGPT-like UI** — Clean, dark-mode interface with centered chat, suggestion chips, and smooth animations.
- **Multi-file Intelligence** — Support for CSV, PDF, Excel, and Word files via LlamaIndex and Neon pgvector.
- **Hybrid Retrieval** — Semantic search combined with BM25 keyword matching for pinpoint accuracy.
- **Live Market Data** — Real-time stock prices, income statements, and balance sheets via yfinance.
- **Interactive Charts** — Auto-generated Plotly/HTML charts visualized directly in the chat.
- **Persistent Memory** — Full conversation history saved to SQLite, allowing you to resume any thread.
- **LangGraph Agent** — Robust ReAct agent architecture with specialized nodes for Finance, Web Search, and Knowledge Retrieval.

---

## 📂 Project Structure

```text
cfobuddy/
├── api/                     ← FastAPI backend implementation
│   ├── main.py              ← REST API entry point
│   └── ...
├── frontend/                ← Next.js 15+ ChatGPT-style interface
│   ├── src/app/             ← App router (Dashboard, Landing)
│   ├── src/components/      ← ChatArea, Sidebar, etc.
│   └── ...
├── core/                    ← Agent logic, Graph, and LLM setup
├── tools/                   ← Finance, Chart, and Search tools
├── data/                    ← Local knowledge base (PDFs, CSVs)
├── build_index.py           ← Indexing script for local data
└── requirements.txt         ← Backend dependencies
```

---

## 🚀 Quick Start

### 1. Backend Setup

```bash
# Clone and enter
git clone https://github.com/caffeicsatyam/cfobuddy.git
cd cfobuddy

# Virtual environment
python -m venv venv
source venv/bin/activate  # venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the root:

```env
# LLM
GROQ_API_KEY=your_groq_api_key

# Vector DB (Neon)
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require

# Financial APIs
TWELVE_DATA_API_KEY=your_twelve_data_key
```

### 3. Build Index & Run

```bash
# 1. Initialize Vector DB (Run once)
python build_index.py

# 2. Start Backend API
python main.py
```

### 4. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Visit **[http://localhost:3000](http://localhost:3000)** to see the new CFO Buddy!

---

## 🛠 Tools & Tech Stack

| Component | Technology |
|-----------|------------|
| **LLM** | Groq (Llama 3 / Mixtral) |
| **Orchestration** | LangGraph |
| **Vector DB** | Neon (PostgreSQL + pgvector) |
| **Framework** | FastAPI (Backend) / Next.js (Frontend) |
| **Search** | LlamaIndex + BM25 |
| **Charts** | Plotly + HTML Components |

---

## 📈 Roadmap

- [x] Human-like ChatGPT UI redesign
- [x] Multi-agent Graph Architecture
- [x] Interactive Chart Visualization
- [ ] Per-user Vector Stores
- [ ] Direct Bank Integration (Plaid)
- [ ] Voice interface support

---

## 📄 License

MIT © [caffeicsatyam](https://github.com/caffeicsatyam)
