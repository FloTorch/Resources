# Agent Evaluation – CLI Guide

This guide explains how to run agent evaluations from the command line. Agent evaluations score tool-using agents on goal achievement, response coherence, and tool call accuracy.

**Installation:** `pip install floeval` (standard) or `pip install floeval[flotorch]` for FloTorch-hosted agents.  
**FloTorch Console:** [https://docs.flotorch.cloud/introduction/](https://docs.flotorch.cloud/introduction/)

**Provider flexibility:** You can use any OpenAI-compatible provider. For FloTorch-hosted agents, use the FloTorch gateway URL and keys from the [FloTorch Console](https://docs.flotorch.cloud/introduction/).

---

## Evaluation Modes

| Mode | Description | CLI usage |
|------|-------------|-----------|
| **Mode 1** | Pre-captured traces in dataset | Full dataset with `trace` field |
| **Mode 3** | FloTorch-hosted agent | Partial dataset + `agent_name` in config |

Mode 2 (local agent) is only available from Python, not CLI.

---

## 1. Prepare the Agent Dataset

### Full Dataset (Mode 1 – Pre-captured traces)

Save as `agent_full.json`:

```json
{
  "samples": [
    {
      "user_input": "Get the weather for London",
      "reference_outcome": "Provides London weather",
      "reference_tool_calls": [{"name": "get_weather", "args": {"city": "London"}}],
      "trace": {
        "messages": [
          {"role": "human", "content": "Get the weather for London"},
          {"role": "ai", "content": "", "tool_calls": [{"name": "get_weather", "args": {"city": "London"}}]},
          {"role": "tool", "content": "Sunny, 22°C", "tool_name": "get_weather"},
          {"role": "ai", "content": "The weather in London is sunny with 22°C."}
        ],
        "final_response": "The weather in London is sunny with 22°C."
      }
    }
  ]
}
```

- `user_input` — required
- `trace` — required for full datasets; messages with roles `human`, `ai`, `tool`
- `reference_outcome` — optional; helps goal_achievement
- `reference_tool_calls` — optional; required for tool_call_accuracy

### Partial Dataset (Mode 3 – FloTorch hosted)

Save as `agent_partial.json`:

```json
{
  "samples": [
    {
      "user_input": "What is the weather in Tokyo?",
      "reference_outcome": "Provides Tokyo weather",
      "reference_tool_calls": [{"name": "get_weather", "args": {"city": "Tokyo"}}]
    }
  ]
}
```

---

## 2. Prepare the Config File

### Mode 1 (Pre-captured)

Save as `agent_config.yaml`:

```yaml
llm_config:
  base_url: "https://api.openai.com/v1"
  api_key: "YOUR_API_KEY"
  chat_model: gpt-4o-mini
  embedding_model: text-embedding-3-small

evaluation_config:
  default_provider: "builtin"
  metrics:
    - goal_achievement
    - response_coherence
```

### Mode 3 (FloTorch hosted)

Add `agent_name` to evaluation_config:

```yaml
llm_config:
  base_url: "https://gateway.flotorch.cloud/openai/v1"
  api_key: "YOUR_FLOTORCH_API_KEY"
  chat_model: flotorch/turbo

evaluation_config:
  agent_name: "my-agent"
  default_provider: "builtin"
  metrics:
    - goal_achievement
    - response_coherence
```

Requires `pip install floeval[flotorch]`.

---

## 3. Run Agent Evaluation

### Mode 1 (Full dataset)

```bash
floeval evaluate --agent -c agent_config.yaml -d agent_full.json -o agent_results.json
```

### Mode 3 (Partial + FloTorch)

```bash
floeval evaluate --agent -c agent_config_flotorch.yaml -d agent_partial.json -o agent_results.json
```

---

## 4. Available Metrics

| Metric | Provider | Description |
|--------|----------|-------------|
| `goal_achievement` | builtin | Did the agent achieve the goal? (LLM-as-judge) |
| `response_coherence` | builtin | Is the final response consistent with the trace? |
| `ragas:agent_goal_accuracy` | RAGAS | Agent output vs expected outcome |
| `ragas:tool_call_accuracy` | RAGAS | Were tool calls correct? (needs reference_tool_calls) |
