<div align="center">

<div style="background-color: #000000; padding: 20px; border-radius: 10px; display: inline-block; margin: 20px 0;">

# <img src="assets/flotorch_logo.png" alt="FlotorchEval Logo" width="250"/>

</div>

**Practical examples and cookbooks for FlotorchEval**

[![PyPI Version](https://img.shields.io/pypi/v/flotorch-eval?color=blue&label=PyPI&logo=pypi&logoColor=white)](https://pypi.org/project/flotorch-eval/)
[![Python Versions](https://img.shields.io/pypi/pyversions/flotorch-eval?color=blue&logo=python&logoColor=white)](https://pypi.org/project/flotorch-eval/)
[![Documentation](https://img.shields.io/badge/docs-flotorch.ai-blue?logo=read-the-docs&logoColor=white)](https://docs.flotorch.cloud/introduction/)
[![Website](https://img.shields.io/badge/website-flotorch.ai-blue?logo=google-chrome&logoColor=white)](https://flotorch.ai)

[LLM Evaluations](#-llm-evaluations) • [Agent Evaluations](#-agent-evaluations) • [Documentation](https://docs.flotorch.cloud/introduction/)

</div>

---

## 📖 About FlotorchEval

**FlotorchEval** is a comprehensive evaluation framework for the Flotorch ecosystem. It enables evaluation of both **LLM outputs** using industry-standard metrics from DeepEval and Ragas, and **agent behaviors** using custom metrics, with support for OpenTelemetry traces and advanced cost/usage analysis.

### Key Capabilities

- 🎯 **LLM Evaluation**: Multi-engine support (DeepEval & Ragas) with RAG metrics, faithfulness, context relevancy, and more
- 🤖 **Agent Evaluation**: Custom evaluation framework for agent trajectories with goal accuracy, tool call tracking, and performance metrics
- 📊 **Gateway Metrics**: Automatic tracking of latency, cost, and token usage
- 🔌 **Flexible Architecture**: Pluggable metric system with configurable thresholds

> 📚 **Full Documentation**: Visit [docs.flotorch.cloud](https://docs.flotorch.cloud/introduction/) for complete API reference and guides

---

## 📚 Notebook Collections

This repository contains practical, hands-on notebooks demonstrating how to use FlotorchEval for different evaluation scenarios. Each notebook includes complete code examples, explanations, and best practices.

### 🎯 LLM Evaluations

Comprehensive notebooks for evaluating LLM outputs, RAG systems, and retrieval pipelines using industry-standard metrics.

**[📂 View LLM Evaluation Notebooks →](llm-evaluations/)**

| Category | Description |
|:--------|:-----------|
| **RAG Evaluation** | Evaluate RAG pipelines with faithfulness, answer relevance, and context metrics |
| **Advanced Metrics** | Deep dive into multi-engine evaluation with DeepEval and Ragas |
| **Gateway Metrics** | Track and analyze latency, cost, and token usage from LLM calls |

### 🤖 Agent Evaluations

Notebooks demonstrating agent trajectory evaluation, tool usage analysis, and goal achievement metrics using OpenTelemetry traces.

**[📂 View Agent Evaluation Notebooks →](agent_evaluations/)**

| Category | Description |
|:--------|:-----------|
| **Trajectory Analysis** | Evaluate agent behavior and decision-making processes |
| **Tool Call Accuracy** | Assess tool usage and appropriateness |
| **Goal Achievement** | Measure if agents successfully accomplish intended goals |
| **Performance Metrics** | Track latency, cost, and resource usage for agent workflows |

---

## 🚀 Quick Start

### Installation

```bash
pip install flotorch-eval
```

### Basic Usage

**LLM Evaluation:**
```python
from flotorch_eval.llm_eval import LLMEvaluator, EvaluationItem

evaluator = LLMEvaluator(
    api_key="your-api-key",
    base_url="flotorch-base-url",
    evaluator_llm="flotorch/inference_model",
    embedding_model="flotorch/embedding_model"
)

data = [EvaluationItem(
    question="What is machine learning?",
    generated_answer="Machine learning is...",
    expected_answer="Machine learning is...",
    context=["Context documents..."]
)]

results = evaluator.evaluate(data=data)
```

**Agent Evaluation:**
```python
from flotorch_eval.agent_eval import AgentEvaluator

client = AgentEvaluator(
    api_key="your-api-key",
    base_url="flotorch-base-url",
    default_evaluator="flotorch/inference_model"
)

trace = client.fetch_traces(trace_id="your-trace-id")
results = await client.evaluate(trace=trace)
```

---

## 📖 Resources

- 📚 [Full Documentation](https://docs.flotorch.cloud/introduction/)
- 🌐 [Website](https://flotorch.ai)
- 📦 [PyPI Package](https://pypi.org/project/flotorch-eval/)
- 💻 [GitHub Repository](https://github.com/FloTorch/flotorch-eval)

---

## 🤝 Contributing

We welcome contributions! If you'd like to add new evaluation notebooks or improve existing ones, please see our [Contributing Guidelines](CONTRIBUTING.md).

---

<div align="center">

**Made with ❤️ by the Flotorch Team**

[Website](https://flotorch.ai) • [Documentation](https://docs.flotorch.cloud/introduction/) • [PyPI](https://pypi.org/project/flotorch-eval/) • [GitHub](https://github.com/FloTorch/flotorch-eval)

</div>
