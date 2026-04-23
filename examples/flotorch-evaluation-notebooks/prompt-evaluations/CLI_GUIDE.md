# Prompt Evaluation – CLI Guide

This guide explains how to run prompt evaluations from the command line. Prompt evaluations compare different system instructions (prompts) on the same questions. Floeval generates a response for each (question, prompt) pair and scores them.

**Provider flexibility:** You can use any OpenAI-compatible provider (OpenAI, Azure OpenAI, Anthropic, local models, etc.). For FloTorch keys and gateway, use the [FloTorch Console](https://docs.flotorch.cloud/introduction/).

---

## 1. Create the Prompts File

Define each prompt variant in a YAML file. Each prompt needs a `template` field (the system instruction).

Save as `prompts.yaml`:

```yaml
prompts:
  concise:
    template: "Answer the question directly and concisely."
  detailed:
    template: "Answer the question with a brief explanation of your reasoning."
```

---

## 2. Prepare the Dataset

Prompt evaluations are **always partial** — Floeval generates responses at runtime. Each sample has `user_input` and `prompt_ids` (which prompts to test).

Save as `prompt_dataset.json`:

```json
{
  "samples": [
    {
      "user_input": "What is the capital of France?",
      "prompt_ids": ["concise", "detailed"]
    },
    {
      "user_input": "What is RAG in machine learning?",
      "prompt_ids": ["concise", "detailed"]
    }
  ]
}
```

This produces 4 evaluations (2 questions × 2 prompts).

---

## 3. Prepare the Config File

Save as `prompt_config.yaml`:

```yaml
llm_config:
  base_url: "https://api.openai.com/v1"
  api_key: "YOUR_API_KEY"
  chat_model: gpt-4o-mini
  embedding_model: text-embedding-3-small

evaluation_config:
  metrics:
    - answer_relevancy
  prompts_file: "prompts.yaml"

dataset_generation_config:
  generator_model: gpt-4o-mini
```

---

## 4. Run Evaluation

```bash
floeval evaluate -c prompt_config.yaml -d prompt_dataset.json -o prompt_results.json
```

Floeval reads the prompts file, generates a response for each (sample, prompt_id) pair, then scores all of them.

---

## 5. Output

Results contain one row per (sample, prompt_id) pair. Each row includes `prompt_id` so you can compare scores across prompts.

---

## 6. Prompt Evaluation with RAG

If your prompts use retrieval context, add `contexts` to each sample and include context-aware metrics:

```yaml
evaluation_config:
  metrics:
    - answer_relevancy
    - faithfulness
  prompts_file: "prompts.yaml"
```
