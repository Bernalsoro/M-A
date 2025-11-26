# Financial RAG Agent

A production-ready Retrieval Augmented Generation (RAG) system with agentic AI capabilities for financial analysis and equity research.

## Overview

This project demonstrates an end-to-end ML engineering pipeline that combines:

- **RAG (Retrieval Augmented Generation)**: Semantic search over financial documents and news
- **Agentic AI**: Autonomous decision-making and tool orchestration
- **Financial Analysis**: Automated computation of key ratios, margins, and comparative metrics
- **Production API**: FastAPI service with complete observability and tracing

The system ingests financial statements and news, creates vector embeddings for semantic search, and orchestrates an intelligent agent that can answer complex financial questions by combining retrieval, numerical computation, and language model reasoning.

## Architecture

```
┌─────────────────┐
│  User Question  │
│  + Ticker(s)    │
└────────┬────────┘
         │
         ▼
┌────────────────────────────────────────┐
│         FastAPI Endpoint               │
│         POST /ask                      │
└────────┬───────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────┐
│      Financial Agent                   │
│  ┌──────────────────────────────────┐  │
│  │  1. Planner                      │  │
│  │     - Analyze question           │  │
│  │     - Decide tool sequence       │  │
│  └──────────────────────────────────┘  │
│  ┌──────────────────────────────────┐  │
│  │  2. Tool Executor                │  │
│  │     - fetch_financials()         │  │
│  │     - compute_ratios()           │  │
│  │     - retrieve_context()         │  │
│  │     - compare_two_tickers()      │  │
│  └──────────────────────────────────┘  │
│  ┌──────────────────────────────────┐  │
│  │  3. LLM Synthesizer              │  │
│  │     - Combine numerical data     │  │
│  │     - Integrate retrieved text   │  │
│  │     - Generate analyst-style ans │  │
│  └──────────────────────────────────┘  │
└────────┬───────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────┐
│  Data Layer                            │
│  ┌──────────────┐  ┌────────────────┐  │
│  │ Financials   │  │ Vector Store   │  │
│  │ (CSV)        │  │ (FAISS)        │  │
│  │ - Balance    │  │ - News         │  │
│  │ - P&L        │  │ - Summaries    │  │
│  │ - Ratios     │  │ - Context      │  │
│  └──────────────┘  └────────────────┘  │
└────────────────────────────────────────┘
```

## Project Structure

```
financial-rag-agent/
├── README.md
├── pyproject.toml
├── src/
│   └── financial_rag_agent/
│       ├── __init__.py
│       ├── config.py              # Configuration management
│       ├── data/
│       │   ├── sample_financials.csv
│       │   └── sample_news.json
│       ├── ingestion/
│       │   ├── loader.py          # Data loading utilities
│       │   └── preprocessor.py    # Data cleaning and transformation
│       ├── retrieval/
│       │   ├── vector_store.py    # FAISS vector database
│       │   └── retriever.py       # Semantic search interface
│       ├── llm/
│       │   ├── llm_client.py      # LLM provider abstraction
│       │   └── prompts.py         # Prompt templates
│       ├── agents/
│       │   ├── tools.py           # Agent tool implementations
│       │   ├── planner.py         # Task planning logic
│       │   └── agent.py           # Main agent orchestrator
│       ├── api/
│       │   └── main.py            # FastAPI application
│       └── evaluation/
│           ├── metrics.py         # Evaluation metrics
│           └── eval_examples.py   # Test cases
├── notebooks/
│   └── demo_financial_rag.ipynb   # Interactive demo
└── tests/
    ├── test_retrieval.py
    ├── test_agent.py
    └── test_api.py
```

## Installation

### Prerequisites

- Python 3.10 or higher
- pip or uv package manager

### Setup

1. **Clone the repository**:
```bash
cd financial-rag-agent
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -e ".[dev]"
```

4. **Configure environment variables**:
Create a `.env` file in the project root:
```env
# LLM Configuration
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
LLM_PROVIDER=openai  # or anthropic

# Model Selection
OPENAI_MODEL=gpt-4-turbo-preview
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# Embedding Model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Application Settings
LOG_LEVEL=INFO
```

## Usage

### 1. Initialize the Vector Store

Before using the agent, you need to index the financial data:

```bash
python -m financial_rag_agent.ingestion.loader
```

This will:
- Load financial statements from CSV
- Load news summaries from JSON
- Create embeddings
- Build FAISS index

### 2. Start the API Server

```bash
uvicorn financial_rag_agent.api.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### 3. Query the Agent

**Via API**:
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "AAPL",
    "question": "Analyze the recent earnings and comment on margin trends"
  }'
```

**Via Python**:
```python
from financial_rag_agent.agents.agent import FinancialAgent

agent = FinancialAgent()
result = agent.answer(
    ticker="AAPL",
    question="Compare profitability metrics with MSFT"
)

print(result["final_answer"])
print(f"Tools used: {result['used_tools']}")
```

**Via Demo Notebook**:
```bash
jupyter notebook notebooks/demo_financial_rag.ipynb
```

### 4. Run Tests

```bash
pytest tests/ -v --cov=financial_rag_agent
```

## Example Queries

### Single Company Analysis
```json
{
  "ticker": "AAPL",
  "question": "What are the key financial metrics and recent performance highlights?"
}
```

### Comparative Analysis
```json
{
  "ticker": "AAPL",
  "question": "Compare Apple's margins and growth with Microsoft over the last year"
}
```

### Risk Assessment
```json
{
  "ticker": "NVDA",
  "question": "What are the main risks for NVIDIA based on recent news and financial position?"
}
```

## API Reference

### POST /ask

Submits a financial question to the agent.

**Request Body**:
```json
{
  "ticker": "AAPL",
  "question": "Your financial question here",
  "context_limit": 5  // optional, max retrieved documents
}
```

**Response**:
```json
{
  "answer": "Detailed analyst-style response...",
  "plan": ["compute_ratios", "retrieve_context", "compose_summary"],
  "used_tools": ["compute_ratios", "retrieve_context"],
  "retrieved_docs": [
    {
      "content": "Apple beats earnings...",
      "metadata": {"ticker": "AAPL", "date": "2024-10-30"},
      "score": 0.89
    }
  ],
  "execution_time_ms": 1250
}
```

### GET /health

Health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "vector_store_loaded": true,
  "model_available": true
}
```

## How This Maps to ML Engineering (RAG & Agents)

### 1. **RAG Pipeline Design**
- **Ingestion**: Structured (CSV) and unstructured (JSON) data preprocessing
- **Embedding**: Converting financial text to dense vectors using transformer models
- **Indexing**: Efficient similarity search with FAISS
- **Retrieval**: Context-aware document fetching based on query semantics

### 2. **Agentic AI Architecture**
- **Planning**: Question decomposition and tool selection strategy
- **Tool Use**: Discrete actions (fetch data, compute metrics, search documents)
- **Orchestration**: Multi-step reasoning with state management
- **Observability**: Complete tracing of agent decisions and tool calls

### 3. **Production Engineering**
- **API Design**: RESTful interface with proper error handling
- **Configuration Management**: Environment-based settings
- **Testing**: Unit and integration tests for all components
- **Modularity**: Clean separation of concerns for maintainability

### 4. **Domain Expertise**
- **Financial Metrics**: Proper computation of ratios, margins, leverage
- **Analyst Workflow**: Mimics real equity research processes
- **Data Quality**: Validation and preprocessing of financial data

## Future Extensions

This project can be extended to demonstrate additional ML engineering skills:

1. **Advanced RAG**:
   - Hybrid search (dense + sparse/BM25)
   - Re-ranking models
   - Query expansion and decomposition

2. **Fine-tuning**:
   - Fine-tune embeddings on financial text
   - Fine-tune LLM for financial reasoning
   - RLHF for better analyst-style outputs

3. **Evaluation**:
   - Automated benchmarks (LLM-as-judge)
   - Retrieval metrics (MRR, NDCG)
   - Faithfulness and hallucination detection

4. **Production**:
   - Docker containerization
   - Cloud deployment (AWS/GCP)
   - Monitoring and logging (Prometheus, Grafana)
   - Caching layer (Redis)

5. **Data Sources**:
   - SEC EDGAR filings integration
   - Real-time market data feeds
   - Transcript analysis (earnings calls)

6. **Multi-agent Systems**:
   - Specialized agents (macro, sector, single-stock)
   - Agent collaboration and consensus
   - Tool learning and adaptation

## License

MIT License - See LICENSE file for details

## Contributing

This is a demonstration project for technical interviews. For questions or suggestions, please open an issue.

## Contact

For questions about this project or ML engineering roles, please reach out via GitHub issues.
