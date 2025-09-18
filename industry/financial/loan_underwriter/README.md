# 🏦 Loan Underwriter: Agentic LLM Pipeline with MCP + LangGraph + FloTorch

This project implements an LLM-powered loan underwriting pipeline using:

- 🤖 **LangGraph** for multi-step orchestration
- 🛠 **MCP servers** (Model Context Protocol) as LLM-powered tools
- 🧠 **Agent prompt modules** for clean, reusable prompt engineering
- 📡 **FloTorch AI Gateway** for governed LLM hosting, observability, and tracing

---

## Pre-requisities

1. Configure Flotorch model to be accessed via agents.
2. Generate Flotorch gateway key. 

## 💡 Overview

This is a modular, agentic system that processes a loan application through 3 roles:

1. **Loan Officer** ➝ Summarizes the application
2. **Credit Analyst** ➝ Evaluates creditworthiness
3. **Risk Manager** ➝ Makes a final approval/denial decision

Each role is:

- Deployed via a dedicated **MCP server** (in `agents/`)
- Orchestrated with **LangGraph** (in `langgraph_flow/`)

---

## 🧱 Project Structure

```bash
loan_underwriter/
├── agents/
│   ├── loan_parser/
│   ├── credit_analyzer/
│   └── risk_assessor/
│
├── backend/
│   └── app.py # FastAPI web server on Langgraph flow 
│
├── common/
│   └── flotorch_chat_model.py # 
│
├── data/
│   └── loan_application_history.csv
│
├── frontend/
│   └── app.py # Uses Streamlit
│
├── langgraph_flow/
│   └── graph.py
│
├── .env
└── README.md
```

---

## 🛠️ Requirements

- Python 3.10+
- Docker
- [FloTorch](https://flotorch.ai)

---

## 🚀 Getting Started

### 1. Set environment variables

1. Make a copy of the `.env.example`, and update the keys. The following list is NOT exhaustive please refer to the latest `.env.example` file.

#### `.env`

```env
FLOTORCH_API_KEY=<YOUR_FLOTORCH_API_KEY>    # for LLM access
FLOTORCH_MODEL=<YOUR_FLOTORCH_MODEL>        # the model you created through FloTorch
```

### 2. Start app

```bash
make start
```

or

```bash
docker compose up --build
```

### 3. Apply for loan

- Fill out the loan application form in [Streamlit](http://localhost:8501)
- Submit and wait for result

Check logs in:

- 🔍 [FloTorch console](console.flotorch.cloud) for full trace

---

## ✨ Key Concepts

### ✅ Agents

Each agent is has:

- Defined role and task in `prompt.py`
- Input and output types in `model.py`
- MCP server in `main.py`
- LLM client in `utils.py`

### ✅ MCP Servers

Each server exposes a single `/process` endpoint that:

- Receives structured input
- Crates role-specific prompt
- Sends the prompt to the FloTorch AI Gateway
- Returns structured output

### ✅ LangGraph

Handles orchestration across:

- `LoanParser` ➝ `CreditAnalyzer` ➝ `RiskAssessor`
- Passes structured state between nodes

### ✅ FloTorch

Access all kinds of reasoning models through one endpoint.

- `FlotorchLLM` - model access point provided by the [FloTorch SDK](https://github.com/FloTorch/Resources/tree/main/examples/flotorch-sdk%20notebooks)
- `ChatFloTorch` - LangGraph wrapper for FloTorch
- Monitor token use, latency, caching, guardrails, and more in the [FloTorch console](console.flotorch.cloud)

---

## 📦 Possible Next Steps

- Fine-tuned LLMs for better decision accuracy
- MCP tools for background checks

---
