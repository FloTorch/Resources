# LLM Evaluation – CLI Guide

This guide explains how to run LLM evaluations from the command line. You will prepare a dataset file, a config file, and then run `floeval evaluate`.

**Installation:** `pip install floeval`

**Provider flexibility:** You can use any OpenAI-compatible provider (OpenAI, Azure OpenAI, Anthropic, local models, etc.). For FloTorch keys and gateway, use the [FloTorch Console](https://docs.flotorch.cloud/introduction/).

---

## 1. Prepare the Dataset

Floeval expects a JSON or JSONL file with a `samples` array. Each sample must have `user_input` (the question). For full datasets, each sample must also have `llm_response` (the model's answer).

### Full Dataset (you already have responses)

Save as `llm_full_dataset.json`:

```json
{
  "samples": [
    {
      "user_input": "What is Python?",
      "llm_response": "Python is a programming language.",
      "ground_truth": "A programming language"
    },
    {
      "user_input": "What is RAG?",
      "llm_response": "RAG stands for Retrieval-Augmented Generation.",
      "ground_truth": "Retrieval-Augmented Generation"
    }
  ]
}
```

- `user_input` — required; the question or prompt
- `llm_response` — required for full datasets; the model's answer
- `ground_truth` — optional; used by some metrics

### Partial Dataset (let Floeval generate responses)

Save as `llm_partial_dataset.json`:

```json
{
  "samples": [
    { "user_input": "What is Python?" },
    { "user_input": "What is RAG?" }
  ]
}
```

Omit `llm_response`. Floeval will call your LLM to generate responses, then score them.

---

## 2. Prepare the Config File

Save as `llm_config.yaml`:

```yaml
llm_config:
  base_url: "https://api.openai.com/v1"
  api_key: "YOUR_API_KEY"
  chat_model: gpt-4o-mini
  embedding_model: text-embedding-3-small

evaluation_config:
  default_provider: "ragas"
  metrics:
    - answer_relevancy

# Required only for partial datasets
dataset_generation_config:
  generator_model: gpt-4o-mini
```

Replace `YOUR_API_KEY` with your actual API key, or use an environment variable in your config loader.

---

## 3. Run Evaluations

### Full dataset

```bash
floeval evaluate -c llm_config.yaml -d llm_full_dataset.json -o llm_results.json
```

### Partial dataset (generate + evaluate in one step)

```bash
floeval evaluate -c llm_config.yaml -d llm_partial_dataset.json -o llm_results.json
```

Floeval auto-detects partial datasets and generates responses before scoring.

### Two-step: generate first, then evaluate

```bash
floeval generate -c llm_config.yaml -d llm_partial_dataset.json -o llm_completed.json
floeval evaluate -c llm_config.yaml -d llm_completed.json -o llm_results.json
```

---

## 4. Output

The output JSON contains:

- `sample_results` — per-sample scores and metadata
- `aggregate_scores` — mean score per metric across all samples
- `summary` — total samples, providers used, pass rates

---

## 5. Available Metrics

| Metric ID | Provider | Description |
|-----------|----------|-------------|
| `answer_relevancy` | ragas | How relevant the answer is to the question |
| `deepeval:answer_relevancy` | deepeval | Answer relevance (DeepEval implementation) |

Use `ragas:answer_relevancy` or `deepeval:answer_relevancy` when you want to specify the provider explicitly.
