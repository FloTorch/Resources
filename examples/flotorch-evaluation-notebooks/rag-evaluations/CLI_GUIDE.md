# RAG Evaluation – CLI Guide

This guide explains how to run RAG (Retrieval-Augmented Generation) evaluations from the command line. RAG datasets include `contexts` (retrieved documents) so Floeval can score faithfulness and retrieval quality.

**Installation:** `pip install floeval`

**Provider flexibility:** You can use any OpenAI-compatible provider (OpenAI, Azure OpenAI, Anthropic, local models, etc.). For FloTorch keys and gateway, use the [FloTorch Console](https://docs.flotorch.cloud/introduction/).

---

## 1. Prepare the Dataset

RAG datasets extend the LLM format with a `contexts` field — a list of retrieved document passages for each question.

### Full Dataset (you have responses and contexts)

Save as `rag_full_dataset.json`:

```json
{
  "samples": [
    {
      "user_input": "How does photosynthesis work?",
      "llm_response": "Photosynthesis converts sunlight into energy using chlorophyll in plants.",
      "contexts": [
        "Plants use chlorophyll to capture light.",
        "Converts CO2 and water into glucose and oxygen."
      ],
      "ground_truth": "Converts light into chemical energy"
    }
  ]
}
```

- `user_input` — required
- `llm_response` — required for full datasets
- `contexts` — required for RAG; list of retrieved passages
- `ground_truth` — optional; used by context_precision, context_recall

### Partial Dataset (contexts only, no response)

Save as `rag_partial_dataset.json`:

```json
{
  "samples": [
    {
      "user_input": "What is RAG?",
      "contexts": ["RAG combines document retrieval with language generation."]
    }
  ]
}
```

Floeval generates the response from the question and contexts, then scores it.

---

## 2. Prepare the Config File

Save as `rag_config.yaml`:

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
    - faithfulness

dataset_generation_config:
  generator_model: gpt-4o-mini
```

---

## 3. Run Evaluations

### Full dataset

```bash
floeval evaluate -c rag_config.yaml -d rag_full_dataset.json -o rag_results.json
```

### Partial dataset

```bash
floeval evaluate -c rag_config.yaml -d rag_partial_dataset.json -o rag_results.json
```

---

## 4. Available Metrics

| Metric ID | What it measures |
|-----------|-------------------|
| `answer_relevancy` | How relevant the answer is to the question |
| `faithfulness` | Whether the answer is grounded in the contexts |
| `context_precision` | Whether relevant contexts are ranked first |
| `context_recall` | How much reference info is covered by contexts |

Use `ragas:` or `deepeval:` prefix when the metric exists in multiple providers.
