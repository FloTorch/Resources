<div align="center">

# 🤖 Agent Evaluation Notebooks

**Practical examples for evaluating agent behaviors and trajectories with FlotorchEval**

[![PyPI Version](https://img.shields.io/pypi/v/flotorch-eval?color=blue&label=PyPI&logo=pypi&logoColor=white)](https://pypi.org/project/flotorch-eval/)
[![Documentation](https://img.shields.io/badge/docs-flotorch.ai-blue?logo=read-the-docs&logoColor=white)](https://docs.flotorch.cloud/introduction/)

[← Back to Notebooks](../README.md) • [LLM Evaluations →](../llm-evaluations/README.md)

</div>

---

## 📋 Overview

This collection contains hands-on notebooks demonstrating how to evaluate **agent behaviors** and **trajectories** using FlotorchEval. These notebooks cover various agent evaluation scenarios, from basic trajectory analysis to advanced goal achievement and tool usage metrics.

### What You'll Learn

- ✅ How to set up and configure `AgentEvaluator` for agent evaluation
- ✅ Evaluating agent trajectories using OpenTelemetry traces
- ✅ Measuring goal accuracy and task completion
- ✅ Analyzing tool call accuracy and appropriateness
- ✅ Tracking performance metrics (latency, cost) for agent workflows
- ✅ Comparing agent performance against reference trajectories
- ✅ Best practices for agent evaluation workflows

---

## 📚 Available Notebooks

| # | Notebook | Description | Run in Colab |
|:--|:---------|:-----------|:------------:|
| *Coming Soon* | More notebooks will be added here | Check back soon for agent evaluation examples | - |

> 💡 **Note**: Agent evaluation notebooks are being actively developed. Check back soon for practical examples!

---

## 🎯 Evaluation Capabilities

### Trajectory Analysis

Evaluate agent behavior by analyzing the complete trajectory of actions, decisions, and outcomes from OpenTelemetry traces.

**Key Features**:
- 📈 Complete trajectory reconstruction from traces
- 🧠 LLM-based trajectory quality assessment
- ✅ Goal inference and completion validation
- 📊 Step-by-step behavior analysis

---

### Tool Call Evaluation

Assess the accuracy and appropriateness of tool calls made by agents throughout their execution.

**Key Features**:
- 🛠️ Tool usage pattern analysis
- ✅ Tool call correctness validation
- 📊 Tool selection appropriateness
- 🔍 Missing tool call detection

---

### Goal Achievement Metrics

Measure whether agents successfully accomplish their intended goals and tasks.

**Key Features**:
- 🎯 Goal perception evaluation
- 📋 Plan soundness assessment
- ⚙️ Execution coherence analysis
- ✅ Final outcome validation

---

### Performance Metrics

Track operational metrics including latency, cost, and resource usage for agent workflows.

**Key Features**:
- ⚡ Total and average latency tracking
- 💰 Cost analysis per agent run
- 📊 Token usage monitoring
- 🔄 Hierarchical latency breakdown

---

## 🔧 Common Evaluation Patterns

### Basic Agent Evaluation

```python
from flotorch_eval.agent_eval import AgentEvaluator

# Initialize the evaluation client
client = AgentEvaluator(
    api_key="your-api-key",
    base_url="flotorch-base-url",
    default_evaluator="flotorch/inference_model"
)

# Fetch trace data from Flotorch API
trace = client.fetch_traces(trace_id="your-trace-id")

# Evaluate with all default metrics
results = await client.evaluate(trace=trace)

# Access results
for metric_result in results.scores:
    print(f"Metric: {metric_result.name}, Score: {metric_result.score}")
    print(f"Details: {metric_result.details}")
```

### Custom Metrics Evaluation

```python
from flotorch_eval.agent_eval.metrics.llm_evaluators import (
    TrajectoryEvalWithLLM,
    ToolCallAccuracy,
    AgentGoalAccuracy
)
from flotorch_eval.agent_eval.metrics.latency_metrics import LatencyMetric
from flotorch_eval.agent_eval.metrics.usage_metrics import UsageMetric

# Define custom metrics
custom_metrics = [
    TrajectoryEvalWithLLM(),
    ToolCallAccuracy(),
    AgentGoalAccuracy(),
    LatencyMetric(),
    UsageMetric()
]

# Evaluate with specific metrics
trace = client.fetch_traces(trace_id="your-trace-id")
results = await client.evaluate(trace=trace, metrics=custom_metrics)
```

### Reference Trajectory Comparison

```python
# Define a reference trajectory
reference_trajectory = {
    "input": "What is AWS Bedrock?",
    "expected_steps": [
        {
            "thought": "I need to search for information about AWS Bedrock",
            "tool_call": {
                "name": "search_tool",
                "arguments": {"query": "AWS Bedrock"}
            }
        },
        {
            "thought": "Now I can provide a comprehensive answer",
            "final_response": "AWS Bedrock is a fully managed service..."
        }
    ]
}

# Evaluate with reference
trace = client.fetch_traces(trace_id="your-trace-id")
results = await client.evaluate(
    trace=trace,
    reference=reference_trajectory
)
```

### Working with Flotorch Agents

```python
from flotorch.adk.agent import FlotorchADKAgent

# Initialize agent client
agent_client = FlotorchADKAgent(
    agent_name="your-agent-name",
    base_url="flotorch-base-url",
    api_key="your-api-key"
)

# Get trace IDs from agent
trace_ids = agent_client.get_tracer_ids()

# Evaluate each trace
for trace_id in trace_ids:
    trace = client.fetch_traces(trace_id=trace_id)
    results = await client.evaluate(trace=trace)
    print(f"Evaluation results for trace {trace_id}: {results}")
```

---

## 📊 Available Metrics

| Metric | Description | Requires LLM |
|:------:|:------------|:------------:|
| `TrajectoryEvalWithLLM` | Evaluates agent trajectory quality by inferring the agent's goal from its actions and assessing whether it was successfully completed. Returns a binary score (0 or 1) with detailed explanation. | ✅ Yes |
| `TrajectoryEvalWithLLMWithReference` | Compares agent trajectory against a reference trajectory to evaluate performance. Requires a reference trajectory to be provided. | ✅ Yes |
| `ToolCallAccuracy` | Assesses the accuracy and appropriateness of tool calls made by the agent. Evaluates whether tools were used correctly and when they should have been used. | ✅ Yes |
| `AgentGoalAccuracy` | Validates if the agent successfully accomplished the user's intended goal. Evaluates goal perception, plan soundness, execution coherence, and final outcome. | ✅ Yes |
| `LatencyMetric` | Tracks latency metrics including total latency, average step latency, and hierarchical latency breakdown across all steps in the trajectory. | ❌ No |
| `UsageMetric` | Monitors cost and token usage. Provides total cost, average cost per call, and detailed cost breakdown per model and span. | ❌ No |

> **Default Metrics**: When no metrics are specified, the evaluator uses all available metrics by default: `TrajectoryEvalWithLLM`, `ToolCallAccuracy`, `AgentGoalAccuracy`, `UsageMetric`, and `LatencyMetric`. If a reference is provided, `TrajectoryEvalWithLLMWithReference` is automatically added.

---

## 🚀 Getting Started

1. **Install FlotorchEval**:
   ```bash
   pip install flotorch-eval
   ```

2. **Set Up Flotorch Agent**: Ensure you have a Flotorch agent configured and running

3. **Get Trace IDs**: Retrieve trace IDs from your agent executions

4. **Run Evaluation**: Use the `AgentEvaluator` to fetch traces and evaluate agent behavior

5. **Analyze Results**: Review metric scores and detailed evaluation information

---

## 📖 Additional Resources

- 📚 [FlotorchEval Documentation](https://docs.flotorch.cloud/introduction/)
- 🔗 [Main Notebooks README](../README.md)
- 🎯 [LLM Evaluation Notebooks](../llm-evaluations/README.md)
- 🌐 [Flotorch Website](https://flotorch.ai)

---

## 🤝 Contributing

Found a bug or want to add a new agent evaluation notebook? We welcome contributions! Please see our [Contributing Guidelines](../CONTRIBUTING.md).

---

<div align="center">

**Made with ❤️ by the Flotorch Team**

[Website](https://flotorch.ai) • [Documentation](https://docs.flotorch.cloud/introduction/) • [PyPI](https://pypi.org/project/flotorch-eval/)

</div>

