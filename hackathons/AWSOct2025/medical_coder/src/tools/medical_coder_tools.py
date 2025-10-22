from strands import tool
from pinecone import Pinecone, SearchQuery
from utils.config import settings

# Bypass tool consent, like permission for writing files
import os
os.environ["BYPASS_TOOL_CONSENT"] = "true"

pc = Pinecone(api_key=settings.pinecone_api_key)

# Pinecone semantic search function
@tool
def search_codes_medical(index_name: str, query: str, top_k: int = 10):
    """Search specified medical code Pinecone index for codes with semantically similar descriptions."""
    index = pc.Index(name=index_name)

    search_query: SearchQuery = SearchQuery(
        top_k=top_k,
        inputs={"text": query}
    )

    results = index.search(
        namespace="__default__",
        query=search_query
    )

    hits = []
    for result in results["result"]["hits"]:
        hits.append({
            "code": result["_id"],
            "description": result["fields"].get("description"),
            "score": result["_score"]
        })
    return hits

@tool
def search_codes_icd10cm(query: str, top_k: int = 10):
    """Search the ICD-10-CM Pinecone index for codes with semantically similar descriptions."""
    return search_codes_medical("icd10cm-2026", query, top_k)

@tool
def search_codes_icd10pcs(query: str, top_k: int = 10):
    """Search the ICD-10-PCS Pinecone index for codes with semantically similar descriptions."""
    return search_codes_medical("icd10pcs-2026", query, top_k)

@tool
def search_codes_hcpcs(query: str, top_k: int = 10):
    """Search the HCPCS 2026 Pinecone index for codes with semantically similar descriptions."""
    return search_codes_medical("hcpcs-2026", query, top_k)