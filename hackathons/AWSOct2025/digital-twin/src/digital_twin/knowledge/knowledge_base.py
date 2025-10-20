"""Knowledge Base client for retrieving company information."""

from typing import Dict, Any
from flotorch.sdk.memory import FlotorchVectorStore
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize flotorch vector store once
vector_store = FlotorchVectorStore(
    base_url=os.getenv("FLOTORCH_BASE_URL"),
    api_key=os.getenv("FLOTORCH_API_KEY"),
    vectorstore_id=os.getenv("VECTOR_STORE_ID")
)

class KnowledgeBaseClient:
    """Client for retrieving information from Flotorch Vector Store."""

    def __init__(self) -> None:
        """Initialize the Knowledge Base client."""
        pass

    def retrieve_company_information(self, query: str) -> Dict[str, Any]:
        """Retrieve information from knowledge base.
        
        Args:
            query: User query string
            
        Returns:
            Dictionary containing raw retrieved information and metadata
        """
        try:
            result = vector_store.search(
                query=query,
                max_number_of_result=5
            )
            
            return self._process_flotorch_results(result, query)

        except Exception as e:
            return {
                'success': False,
                'error': f"Vector Store Error: {str(e)}",
                'raw_content': "Unable to retrieve information from knowledge base"
            }
    
    def _process_flotorch_results(self, response: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Process Flotorch Vector Store retrieval results and return raw content."""
        try:
            results = response.get('data', [])
            
            if not results:
                return {
                    'success': False,
                    'error': 'No information found',
                    'raw_content': 'No information found'
                }

            # Extract text content from flotorch response format
            # Each result has a 'content' array with items containing 'text' field
            content_parts = []
            for result in results:
                content_blocks = result.get('content', [])
                for content_block in content_blocks:
                    if isinstance(content_block, dict) and content_block.get('type') == 'text':
                        text = content_block.get('text', '')
                        if text:
                            content_parts.append(text.strip())

            if not content_parts:
                return {
                    'success': False,
                    'error': 'No relevant content found',
                    'raw_content': 'No relevant content found'
                }

            return {
                'success': True,
                'raw_content': '\n\n'.join(content_parts)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error processing results: {str(e)}",
                'raw_content': 'Error processing API response'
            }
    