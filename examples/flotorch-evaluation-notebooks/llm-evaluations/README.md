<div align="center">

# 🎯 LLM Evaluation Notebooks

**Practical examples for evaluating LLM outputs and RAG systems with FlotorchEval**

[![PyPI Version](https://img.shields.io/pypi/v/flotorch-eval?color=blue&label=PyPI&logo=pypi&logoColor=white)](https://pypi.org/project/flotorch-eval/)
[![Documentation](https://img.shields.io/badge/docs-flotorch.ai-blue?logo=read-the-docs&logoColor=white)](https://docs.flotorch.cloud/introduction/)

[← Back to Notebooks](../README.md) • [Agent Evaluations →](../agent_evaluations/README.md)

</div>

---

## 📋 Overview

This collection contains hands-on notebooks demonstrating how to evaluate **LLM outputs** and **RAG (Retrieval-Augmented Generation) systems** using FlotorchEval. These notebooks cover various evaluation scenarios, from basic RAG pipeline evaluation to advanced multi-metric analysis with gateway metrics.

### What You'll Learn

- ✅ How to set up and configure `LLMEvaluator` for different evaluation engines
- ✅ Evaluating RAG systems with industry-standard metrics (faithfulness, answer relevance, context precision, etc.)
- ✅ Using DeepEval and Ragas engines with automatic routing
- ✅ Tracking gateway metrics (latency, cost, token usage)
- ✅ Configuring custom thresholds and metric arguments
- ✅ Best practices for evaluation workflows

---

## 📚 Available Notebooks

| # | Notebook | Description | Run in Colab |
|:--|:---------|:-----------|:------------:|
| 1 | [**Flotorch Assistant Evaluation**](Flotorch_assistant_eval.ipynb) | Evaluate a RAG-based QA system using Flotorch SDK with faithfulness, answer relevancy, context precision, and hallucination metrics | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1DU_V3BAVK4l77OvzGb1bwz9px7yVGhe4) |
| 2 | [**CopilotKit Assistant Evaluation**](copilotKit_assistant_eval.ipynb) | Advanced LLM evaluation with multi-engine support (Ragas & DeepEval) demonstrating faithfulness, answer relevance, context precision, and safety metrics | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/14PoOkvNCF6uaM4kmazWLwWMFxWS0lZT-) |
| 3 | [**Gateway Metrics Evaluation**](08_gateway-metrics.ipynb) | Track and evaluate gateway metrics (latency, cost, token usage) alongside quality metrics for comprehensive system analysis | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1BKGP0flkUBdvX6DRskxToN4C-3RplM0e) |

> 💡 **Tip**: Click on any notebook name to view it on GitHub, or use the Colab badge to run it directly in Google Colab.

---

## 🎯 Evaluation Capabilities

### RAG Pipeline Evaluation

Evaluate RAG systems by measuring how well generated answers align with retrieved context and user questions.

**Key Features**:
- 📊 Faithfulness assessment - Answer consistency with context
- 🎯 Answer relevance - Directness to user questions
- 📚 Context precision - Relevance of retrieved documents
- 🔍 Context recall - Quality of retrieval coverage

---

### Multi-Engine Evaluation

Leverage both DeepEval and Ragas engines with automatic routing for comprehensive evaluation.

**Key Features**:
- 🔄 Auto engine selection with priority-based routing
- 🎯 Hybrid evaluation using both Ragas and DeepEval
- 🛡️ Safety metrics including maliciousness detection
- 📊 Comprehensive multi-metric evaluation workflow

---

### Gateway Metrics Tracking

Monitor operational metrics including latency, cost, and token usage alongside quality metrics.

**Key Features**:
- ⚡ Automatic gateway metrics tracking from Flotorch Gateway
- 💰 Cost analysis and breakdown per model
- ⏱️ Latency tracking (total, average, per-call)
- 📊 Token usage monitoring
- 🔄 Combined quality and operational metrics evaluation

---

## 🔧 Common Evaluation Patterns

### Basic Evaluation Setup

```python
from flotorch_eval.llm_eval import LLMEvaluator, EvaluationItem

evaluator = LLMEvaluator(
    api_key="your-api-key",
    base_url="flotorch-base-url",
    evaluator_llm="flotorch/inference_model",
    embedding_model="flotorch/embedding_model"
)

data = [EvaluationItem(
    question="Your question here",
    generated_answer="Generated answer",
    expected_answer="Expected answer",
    context=["Context documents..."]
)]

results = evaluator.evaluate(data=data)
```

### Auto Engine Selection

```python
evaluator = LLMEvaluator(
    api_key="your-api-key",
    base_url="flotorch-base-url",
    evaluator_llm="flotorch/inference_model",
    embedding_model="flotorch/embedding_model",
    evaluation_engine='auto'  # Automatically routes metrics
)
```

### Custom Metric Thresholds

```python
metric_args = {
    "faithfulness": {"threshold": 0.8},
    "answer_relevance": {"threshold": 0.7},
    "hallucination": {"threshold": 0.3}
}

evaluator = LLMEvaluator(
    api_key="your-api-key",
    base_url="flotorch-base-url",
    evaluator_llm="flotorch/inference_model",
    embedding_model="flotorch/embedding_model",
    metric_args=metric_args
)
```

### Gateway Metrics Integration

```python
from flotorch.sdk.llm import FlotorchLLM

llm = FlotorchLLM(
    model_id="flotorch/gpt-4",
    api_key="your-api-key",
    base_url="flotorch-base-url"
)

response, headers = llm.invoke(
    messages=[{"role": "user", "content": "Your question"}],
    return_headers=True  # Returns gateway metrics
)

eval_item = EvaluationItem(
    question="Your question",
    generated_answer=response.content,
    expected_answer="Expected answer",
    context=["Context..."],
    metadata=headers  # Gateway metrics included
)
```

---

## 📊 Available Metrics

| Metric | Engine | Description |
|:------:|:------:|:------------|
| `FAITHFULNESS` | DeepEval/Ragas | Measures if the answer is factually consistent with the context |
| `ANSWER_RELEVANCE` | DeepEval/Ragas | Evaluates how relevant the answer is to the question |
| `CONTEXT_RELEVANCY` | DeepEval | Assesses if the retrieved context is relevant to the question |
| `CONTEXT_PRECISION` | DeepEval/Ragas | Measures whether retrieved contexts are relevant |
| `CONTEXT_RECALL` | DeepEval | Measures the quality of retrieval |
| `HALLUCINATION` | DeepEval | Detects if the model generates information not in the context |
| `ASPECT_CRITIC` | Ragas | Custom aspect-based evaluation (requires configuration) |
| `LATENCY` | Gateway | Measures total and average latency across LLM calls |
| `COST` | Gateway | Tracks total cost of LLM operations |
| `TOKEN_USAGE` | Gateway | Monitors total token consumption |

---

## 🚀 Getting Started

1. **Install FlotorchEval**:
   ```bash
   pip install flotorch-eval
   ```

2. **Choose a Notebook**: Browse the table above and select a notebook that matches your use case

3. **Open in Colab**: Click the Colab badge to run the notebook directly, or download and run locally

4. **Configure Your Environment**: Update API keys, base URLs, and model identifiers in the notebook

5. **Run and Learn**: Execute the cells step-by-step to understand the evaluation workflow

---

## 📖 Additional Resources

- 📚 [FlotorchEval Documentation](https://docs.flotorch.cloud/introduction/)
- 🔗 [Main Notebooks README](../README.md)
- 🤖 [Agent Evaluation Notebooks](../agent_evaluations/README.md)
- 🌐 [Flotorch Website](https://flotorch.ai)

---

## 🤝 Contributing

Found a bug or want to add a new evaluation notebook? We welcome contributions! Please see our [Contributing Guidelines](../CONTRIBUTING.md).

---

<div align="center">

**Made with ❤️ by the Flotorch Team**

[Website](https://flotorch.ai) • [Documentation](https://docs.flotorch.cloud/introduction/) • [PyPI](https://pypi.org/project/flotorch-eval/)

</div>
