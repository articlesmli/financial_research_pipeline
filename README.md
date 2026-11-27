# Agentic Multi-Model Financial Research & Backtesting Pipeline

An enterprise-grade, institutional-tier multi-agent financial platform built in Python that automates fundamental research, multi-turn adversarial investment committee debates, vector-augmented RAG retrieval, quantitative backtesting, automated PDF tearsheet generation, live WebSocket streaming, and **100% offline CI/CD container deployment**.

Unlike standard LLM wrapper scripts, this platform orchestrates specialised autonomous agents powered by **Ollama** and **LangGraph** that actively debate investment theses over multiple self-correction rounds before passing validated positions into a high-performance **FastAPI** microservice, persistent database logging, and an event-driven quantitative backtesting loop.

---

## What This Project Was For

This project was engineered to bridge the gap between qualitative AI reasoning and rigorous institutional quantitative finance, featuring robust support for isolated, air-gapped server environments:
- **Multi-Turn Autonomous Investment Committee Simulation:** Simulating a hedge fund where a Macro Analyst, Bullish Researcher, and Bearish Devil's Advocate debate market theses through iterative refinement rounds.
- **Vector RAG & SEC Filing Retrieval:** Leveraging ChromaDB to ingest corporate filings and regulatory transcripts so agents ground arguments in real regulatory data.
- **Modern Portfolio Theory (MPT) Optimisation:** Computing optimal asset weights across multi-asset universes using Mean-Variance optimisation via `cvxpy`.
- **Institutional Risk Governance:** Calculating Sortino Ratio, Calmar Ratio, Maximum Drawdown, 95% Daily Value at Risk (VaR), and Conditional Value at Risk (CVaR).
- **Automated PDF Tearsheet Reports:** Instantly generating and downloading publication-ready PDF reports containing full agent verdicts and quantitative backtest metrics.
- **Live WebSocket Streaming:** Broadcasting real-time agent deliberations and progress states directly to clients.
- **Persistent Auditing & Webhooks:** Storing every analysis run and debate transcript in a SQLAlchemy database and dispatching real-time trade signals to webhooks.
- **100% Offline CI/CD & Multipass Deployment:** Fully containerised microservices designed for air-gapped or restricted-network target environments using a local Python wheelhouse and static Docker binaries.

---

## Detailed System Architecture & Data Flow

```text
┌─────────────────┐       HTTP JSON / WebSocket   ┌──────────────────────┐
│ Streamlit UI    │ ────────────────────────────> │ FastAPI Backend      │
│ (:8501)         │ <──────────────────────────── │ (:8001/analyse)      │
└─────────────────┘       Metrics & Reports       └──────────────────────┘
                                                             │
                                                             ▼
                                                  ┌──────────────────────┐
                                                  │ LangGraph Workflow   │
                                                  │ (Multi-Turn Debate)  │
                                                  └──────────────────────┘
                                                             │
                                                             ▼
                                                  ┌──────────────────────┐
                                                  │ ChromaDB Vector RAG  │
                                                  │ & SEC Filings Store  │
                                                  └──────────────────────┘
                                                             │
                                                             ▼
                                                  ┌──────────────────────┐
                                                  │ Quant Backtester     │
                                                  │ (MPT + VaR/CVaR)     │
                                                  └──────────────────────┘
                                                             │
                                                             ▼
                                                  ┌──────────────────────┐
                                                  │ SQLAlchemy Database  │
                                                  │ (Persistent Audit)   │
                                                  └──────────────────────┘

```

---

## Agent Pipeline Breakdown

1. **Macro Data Analyst (`src/agents/graph.py`):** Ingests macroeconomic indicators and market rate summaries via Ollama to establish baseline context.
2. **Bullish Researcher (`src/agents/graph.py`):** Constructs aggressive buy theses backed by earnings growth, market momentum, and RAG document snippets.
3. **Bearish Devil's Advocate (`src/agents/graph.py`):** Proactively stress-tests the bullish thesis against valuation multiples, macro headwinds, and black-swan risk factors.
4. **Risk Manager (`src/agents/graph.py`):** Acts as the final gatekeeper with a **multi-turn feedback loop**, sending theses back to researchers for refinement if risk thresholds are not met.
5. **Backtesting Engine & MPT (`src/backtest/engine.py`):** Executes historical equity curve simulations over Pandas DataFrames to compute Sharpe, Sortino, Calmar ratios, VaR, CVaR, and hit rates.

---

## Comprehensive Project Repository Structure

```text
financial_research_pipeline/
├── .github/
│   └── workflows/              # CI/CD pipelines (GitHub Actions test & Docker push)
├── src/
│   ├── agents/                 # LangGraph state graph and node definitions
│   │   ├── __init__.py
│   │   ├── graph.py            # LangGraph workflow compilation & multi-turn loop
│   │   └── state.py            # Pydantic schemas and AgentState definition
│   ├── backtest/               # Event-driven backtesting engine
│   │   ├── __init__.py
│   │   └── engine.py           # Pandas-based backtester & advanced risk metrics
│   ├── utils/                  # Logging, telemetry, database, RAG, and report utilities
│   │   ├── __init__.py
│   │   ├── alerts.py           # Webhook notification dispatcher
│   │   ├── database.py         # SQLAlchemy ORM models & audit logging
│   │   ├── logger.py           # Centralised logging configuration
│   │   ├── market_data.py      # Historical price data fetcher (yfinance)
│   │   ├── pdf_generator.py    # ReportLab PDF investment report generator
│   │   ├── portfolio_optimizer.py # MPT & Mean-Variance asset weight optimisation
│   │   ├── rag.py              # ChromaDB vector store for SEC filings & transcripts
│   │   └── sec_scraper.py      # Automated SEC EDGAR Form 4 / 10-Q scraper
│   ├── api.py                  # FastAPI backend service endpoints (/analyze, /download-pdf, /audit-logs, /ws/analysis/{ticker})
│   └── app.py                  # Streamlit frontend interactive dashboard
├── wheelhouse/                 # Pre-cached Python 3.11 wheels for 100% offline pip installation
├── tests/                      # Automated test suite
│   └── test_pipeline.py        # Pytest cases for backtesting & optimisation
├── .env                        # Environment configuration (OLLAMA_MODEL / local settings)
├── .gitignore                  # Git ignore rules (.venv/, wheelhouse/, __pycache__)
├── Dockerfile.backend          # Backend container build configuration (offline wheelhouse support)
├── Dockerfile.frontend         # Frontend container build configuration (offline wheelhouse support)
├── docker-compose.yml          # Multi-container orchestration specification
├── deploy.sh                   # Automated deployment script for target VMs
├── requirements.txt            # Pinned Python dependencies
└── README.md                   # Comprehensive project documentation

```

---

## Tech Stack & Core Libraries

* **Orchestration:** LangGraph (Multi-turn stateful agent graphs & memory checkpointing)
* **LLM Provider:** LangChain Ollama (`ChatOllama` / Local LLM)
* **Backend API:** FastAPI & Uvicorn (REST & WebSockets)
* **Frontend UI:** Streamlit & Plotly
* **Vector Store & RAG:** ChromaDB & SEC EDGAR Scraper
* **Portfolio Optimisation:** CVXPY (Modern Portfolio Theory & Efficient Frontier)
* **PDF Generation:** ReportLab
* **Quant & Data Processing:** Pandas, NumPy, yfinance
* **Persistence:** SQLAlchemy & SQLite/PostgreSQL
* **Containerization & CI/CD:** Docker, Docker Compose, Static Binaries, GitHub Actions
* **License:** Open-source MIT License

---

## Quick Start & Deployment Guide

### 1. Set Up Environment Variables

Create a `.env` file in the root directory of your project and configure your local Ollama connection (plus optional webhook URL):

```env
OLLAMA_MODEL=llama3
ALERT_WEBHOOK_URL=[https://hooks.slack.com/services/your/webhook/here](https://hooks.slack.com/services/your/webhook/here)

```

### 2. Local Development Launch

Spin up the application containers using Docker Compose:

```bash
docker compose up --build -d

```

### 3. 100% Offline Multipass / Isolated VM Deployment

For air-gapped environments or isolated Ubuntu VMs (such as a Multipass mock server), use the automated deployment script which leverages a local `wheelhouse/` directory:

```bash
# Execute deployment script from host
./deploy.sh

```

Inside your Dockerfiles, offline installation is enforced via:

```dockerfile
RUN pip install --no-index --find-links=/app/wheelhouse -r requirements.txt

```

### 4. Access the Services

* **Streamlit Interactive Dashboard:** `http://localhost:8501` (or via SSH port forwarding `-L 8501:localhost:8501`)
* **FastAPI Interactive Documentation (Swagger UI):** `http://localhost:8001/docs` (or via SSH port forwarding `-L 8001:localhost:8001`)
* **Audit Logs Endpoint:** `http://localhost:8001/audit-logs`

---

## API Endpoints Reference

| Endpoint | Method | Payload / Params | Description |
| --- | --- | --- | --- |
| `/` | `GET` | None | Welcome message and documentation link. |
| `/health` | `GET` | None | Health check probe for container monitoring. |
| `/audit-logs` | `GET` | None | Retrieves persistent SQLAlchemy session audit logs and past trade metrics. |
| `/analyze` | `POST` | `{"ticker": "AAPL", "initial_capital": 100000, "period": "1mo"}` | Executes multi-turn agent debate, RAG lookup, MPT weights, quantitative backtest, and logs audit data. |
| `/download-pdf` | `POST` | `{"ticker": "AAPL", "initial_capital": 100000, "period": "1mo"}` | Generates and streams an institutional PDF investment committee tearsheet report. |
| `/ws/analysis/{ticker}` | `WebSocket` | Ticker path parameter | Streams real-time agent deliberations and session milestones live to clients. |

---

## License

Distributed under the **MIT License**. See the repository for more details. 

