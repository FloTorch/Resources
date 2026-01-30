# RAG and Memory in Flotorch

## Retrieval-Augmented Generation (RAG)

RAG allows agents to retrieve relevant information from knowledge bases and use it to generate accurate, context-aware responses.

## FlotorchVectorStore

The `FlotorchVectorStore` class provides access to knowledge bases for RAG:

```python
from flotorch.sdk.memory import FlotorchVectorStore

kb = FlotorchVectorStore(
    api_key=FLOTORCH_API_KEY,
    base_url=FLOTORCH_BASE_URL,
    vectorstore_id="your-kb-id"
)
```

## Semantic Search

Perform semantic search to find relevant documents:

```python
# Search for relevant context
context = kb.search("How to create agents?")
results = extract_vectorstore_texts(context)
```

## Creating RAG Tools for Agents

Integrate knowledge base search as a tool for your agent:

```python
from google.adk.tools import FunctionTool

def kb_tool(query: str) -> dict:
    """Search the Flotorch knowledge base for relevant documentation."""
    try:
        context = kb.search(query)
        results = extract_vectorstore_texts(context)
        return {
            "success": True,
            "results": results,
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "results": [],
            "error": str(e)
        }

tools = [FunctionTool(kb_tool)]
```

## Memory Types

Flotorch supports different memory types:

### 1. Vector Store Memory
- Semantic search over documents
- Best for large knowledge bases
- Requires embedding model

### 2. Session Memory
- Conversation history
- Contextual awareness
- Multi-turn conversations

### 3. External Memory
- Integration with external databases
- Custom memory implementations
- Flexible storage options

## Best Practices

1. **Chunking**: Properly chunk documents for optimal retrieval
2. **Metadata**: Add relevant metadata to improve search
3. **Query Optimization**: Craft effective search queries
4. **Result Filtering**: Filter and rank search results
5. **Error Handling**: Handle search failures gracefully

## Performance Tips

- Index documents appropriately
- Use appropriate embedding models
- Implement result caching where possible
- Monitor search latency and optimize queries

