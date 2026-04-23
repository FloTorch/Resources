# Workflow Evaluation – CLI Guide

This guide explains how to run workflow (multi-agent DAG) evaluations from the command line. Workflow evaluations validate pipelines where multiple agents work together in a directed acyclic graph.

**FloTorch Console:** [https://docs.flotorch.cloud/introduction/](https://docs.flotorch.cloud/introduction/)

**Provider flexibility:** Workflow evaluation uses the FloTorch gateway. Obtain credentials from the [FloTorch Console](https://docs.flotorch.cloud/introduction/).

**Prerequisites**

- **Configure agents in the FloTorch Console** — Create and deploy your agents in the [FloTorch Console](https://docs.flotorch.cloud/introduction/) before running workflow evaluation. Each `AGENT` node in the DAG references a deployed agent by name. See [Agent Builder](https://docs.flotorch.cloud/gateway/agents/) and [Workflows](https://docs.flotorch.cloud/gateway/agents/workflows/).
- **Create an API key** — Create an API key in [Settings > API Keys](https://docs.flotorch.cloud/workspace/settings/apikeys/).
- **Install FloTorch integration** — Run `pip install floeval[flotorch]`.

---

## 1. Define the DAG Config

The DAG config specifies the workflow structure. Each `AGENT` node references a deployed agent by name (e.g. `agent1:latest`). Replace these with your actual agent names from the FloTorch Console.

### Example: Sequential workflow

Save as `workflow_dag.json`:

```json
{
  "uid": "sequential-workflow-001",
  "name": "Sequential Workflow",
  "nodes": [
    {"id": "start", "type": "START", "label": "Start"},
    {"id": "agent1", "type": "AGENT", "label": "Agent 1", "agentName": "agent1:latest"},
    {"id": "agent2", "type": "AGENT", "label": "Agent 2", "agentName": "agent2:latest"},
    {"id": "end", "type": "END", "label": "End"}
  ],
  "edges": [
    {"sourceNodeId": "start", "targetNodeId": "agent1"},
    {"sourceNodeId": "agent1", "targetNodeId": "agent2"},
    {"sourceNodeId": "agent2", "targetNodeId": "end"}
  ]
}
```

---

## 2. Prepare the Dataset

Each sample is a test case for the full workflow. Include `user_input` and `reference_outcome`.

Save as `workflow_dataset.json`:

```json
{
  "samples": [
    {
      "user_input": "My order has not arrived after two weeks.",
      "reference_outcome": "An apology and a case escalation to the shipping team."
    },
    {
      "user_input": "What is the status of order #12345?",
      "reference_outcome": "The order is shipped and arriving tomorrow."
    }
  ]
}
```

---

## 3. Prepare the Config File

Save as `workflow_config.yaml`:

```yaml
llm_config:
  base_url: "https://gateway.flotorch.cloud/openai/v1"
  api_key: "YOUR_FLOTORCH_API_KEY"
  chat_model: gpt-4o-mini

evaluation_config:
  metrics:
    - goal_achievement
    - response_coherence
    - ragas:agent_goal_accuracy

agent_workflow_config:
  config:
    uid: "sequential-workflow-001"
    name: "Sequential Workflow"
    nodes:
      - {id: "start", type: "START", label: "Start"}
      - {id: "agent1", type: "AGENT", label: "Agent 1", agentName: "agent1:latest"}
      - {id: "agent2", type: "AGENT", label: "Agent 2", agentName: "agent2:latest"}
      - {id: "end", type: "END", label: "End"}
    edges:
      - {sourceNodeId: "start", targetNodeId: "agent1"}
      - {sourceNodeId: "agent1", targetNodeId: "agent2"}
      - {sourceNodeId: "agent2", targetNodeId: "end"}
```

---

## 4. Run Workflow Evaluation

```bash
floeval evaluate --agent -c workflow_config.yaml -d workflow_dataset.json -o workflow_results.json
```

Floeval reads the DAG definition from the config, runs the workflow for each sample, and scores the results. Results include per-agent traces and overall workflow metrics.
