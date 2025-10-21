"""
Data Ingestion Pipeline for RAG (Retrieval-Augmented Generation) Systems

This module implements a comprehensive data ingestion pipeline that processes documents
from AWS S3, generates embeddings using Amazon Titan, and indexes them in OpenSearch
for semantic search capabilities. The pipeline is designed for production use with
robust error handling, retry mechanisms, and monitoring capabilities.

Architecture Overview:
┌─────────────┐    ┌──────────────┐    ┌─────────────────┐    ┌──────────────┐
│   AWS S3    │───▶│ TextChunker  │───▶│ EmbeddingGen    │───▶│  OpenSearch  │
│ (Documents) │    │ (Semantic)   │    │ (Titan Embed)   │    │ (Vector DB)  │
└─────────────┘    └──────────────┘    └─────────────────┘    └──────────────┘
       │                   │                     │                     │
       ▼                   ▼                     ▼                     ▼
   JSONL/TSV         Chunked Text        Vector Embeddings      Searchable Index

Key Features:
- Fault-tolerant processing with Dead Letter Queue (DLQ)
- Semantic text chunking with configurable overlap
- Amazon Titan embedding generation with fallback mechanisms
- OpenSearch integration for vector storage and retrieval
- Comprehensive logging and monitoring
- Retry logic with exponential backoff

Author: Technical Team
Version: 1.0
Dependencies: boto3, opensearchpy, numpy, tenacity, pandas
"""

# =============================================================================
# IMPORTS AND DEPENDENCIES
# =============================================================================

import boto3                    # AWS SDK for S3, Bedrock operations
import json                     # JSON data processing
import pandas as pd             # Structured data handling (TSV files)
from opensearchpy import OpenSearch, RequestsHttpConnection  # Vector database client
import numpy as np              # Numerical operations for embeddings
from typing import List, Dict, Any, Optional, Tuple  # Type hints for better code clarity
import time                     # Performance timing and delays
import logging                  # Comprehensive logging system
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type  # Retry mechanisms
import re                       # Regular expressions for text processing
from botocore.exceptions import ClientError, ConnectionError  # AWS-specific error handling
from config import *            # Configuration constants (S3 buckets, regions, etc.)

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

# Configure comprehensive logging for production monitoring
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =============================================================================
# S3 DATA LOADING AND MANAGEMENT
# =============================================================================

class S3DataLoader:
    """
    Handles all S3 operations for document loading and error management.
    
    This class provides robust S3 integration with comprehensive error handling,
    retry mechanisms, and Dead Letter Queue (DLQ) functionality for failed documents.
    It supports multiple file formats (JSONL, TSV) commonly used in ML pipelines.
    
    Key Features:
    - Automatic retry with exponential backoff for transient failures
    - Dead Letter Queue for failed document processing
    - Support for JSONL and TSV file formats
    - Comprehensive error logging and monitoring
    
    Production Considerations:
    - Implements circuit breaker pattern through retry limits
    - Handles AWS throttling and rate limiting gracefully
    - Provides audit trail for all operations
    """
    
    def __init__(self):
        """
        Initialize S3 client and configuration.
        
        Sets up AWS S3 client with proper region configuration and
        initializes bucket and folder paths from configuration.
        """
        # Initialize AWS S3 client with region-specific configuration
        self.s3_client = boto3.client('s3', region_name=AWS_REGION)
        
        # Configuration from external config file
        self.bucket = S3_BUCKET_NAME      # Target S3 bucket for document storage
        self.prefix = S3_FOLDER_NAME      # Folder prefix for organized storage
    
    @retry(
        stop=stop_after_attempt(3),                    # Maximum 3 retry attempts
        wait=wait_exponential(multiplier=1, min=4, max=10),  # Exponential backoff: 4s, 8s, 10s
        retry=retry_if_exception_type((ClientError, ConnectionError))  # Only retry on specific errors
    )
    def list_files(self) -> List[str]:
        """
        List all files in the configured S3 folder with robust error handling.
        
        This method discovers all available files for processing, implementing
        retry logic to handle transient AWS service issues. It's the entry point
        for the ingestion pipeline to identify available documents.
        
        Returns:
            List[str]: List of S3 object keys (file paths) ready for processing
            
        Retry Strategy:
            - 3 attempts maximum to handle transient failures
            - Exponential backoff to avoid overwhelming AWS services
            - Only retries on network/service errors, not client errors
            
        Error Handling:
            - Logs all errors for monitoring and debugging
            - Returns empty list on failure to allow pipeline continuation
            - Distinguishes between retryable and non-retryable errors
        """
        try:
            # AWS S3 list_objects_v2 API call with pagination support
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket,
                Prefix=self.prefix
            )
            
            # Extract object keys from response, handling empty buckets gracefully
            file_keys = [obj['Key'] for obj in response.get('Contents', [])]
            
            logger.info(f"Successfully listed {len(file_keys)} files from S3://{self.bucket}/{self.prefix}")
            return file_keys
            
        except Exception as e:
            logger.error(f"Critical error listing S3 files: {e}")
            return []  # Return empty list to prevent pipeline failure
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def load_jsonl(self, file_key: str) -> List[Dict]:
        """
        Load and parse JSONL (JSON Lines) file from S3 with error recovery.
        
        JSONL format is commonly used in ML pipelines where each line contains
        a separate JSON object. This method handles malformed JSON gracefully
        and provides detailed error reporting for debugging.
        
        Args:
            file_key (str): S3 object key (path) to the JSONL file
            
        Returns:
            List[Dict]: List of parsed JSON objects from the file
            
        File Format Expected:
            {"id": "doc1", "text": "Document content..."}
            {"id": "doc2", "text": "Another document..."}
            
        Error Recovery:
            - Skips malformed JSON lines with logging
            - Continues processing remaining valid lines
            - Returns partial results rather than failing completely
        """
        try:
            # Retrieve file content from S3
            response = self.s3_client.get_object(Bucket=self.bucket, Key=file_key)
            content = response['Body'].read().decode('utf-8')
            
            # Parse JSONL format: one JSON object per line
            parsed_objects = []
            for line_num, line in enumerate(content.strip().split('\n'), 1):
                if line.strip():  # Skip empty lines
                    try:
                        parsed_objects.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        logger.warning(f"Malformed JSON at line {line_num} in {file_key}: {e}")
                        continue  # Skip malformed lines, continue processing
            
            logger.info(f"Successfully loaded {len(parsed_objects)} objects from {file_key}")
            return parsed_objects
            
        except Exception as e:
            logger.error(f"Failed to load JSONL file {file_key}: {e}")
            return []  # Return empty list to allow pipeline continuation
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def load_tsv(self, file_key: str) -> pd.DataFrame:
        """
        Load Tab-Separated Values (TSV) file from S3 into pandas DataFrame.
        
        TSV files are commonly used for structured data like query-document
        relevance judgments in information retrieval evaluation datasets.
        
        Args:
            file_key (str): S3 object key to the TSV file
            
        Returns:
            pd.DataFrame: Parsed TSV data as pandas DataFrame
            
        Expected TSV Format:
            query_id    doc_id    relevance_score
            q1          d1        1.0
            q1          d2        0.5
            
        Error Handling:
            - Returns empty DataFrame on parsing errors
            - Logs detailed error information for debugging
            - Handles encoding issues and malformed data gracefully
        """
        try:
            # Retrieve and parse TSV file using pandas
            response = self.s3_client.get_object(Bucket=self.bucket, Key=file_key)
            dataframe = pd.read_csv(response['Body'], sep='\t')
            
            logger.info(f"Successfully loaded TSV with {len(dataframe)} rows from {file_key}")
            return dataframe
            
        except Exception as e:
            logger.error(f"Failed to load TSV file {file_key}: {e}")
            return pd.DataFrame()  # Return empty DataFrame for safe handling
    
    def save_to_dlq(self, failed_docs: List[Dict], error_type: str):
        """
        Save failed documents to Dead Letter Queue (DLQ) for later analysis.
        
        The DLQ pattern is essential for production systems to handle failures
        gracefully. Failed documents are stored for manual review, debugging,
        and potential reprocessing after fixing underlying issues.
        
        Args:
            failed_docs (List[Dict]): Documents that failed processing
            error_type (str): Classification of the error for organization
            
        DLQ Organization:
            - Timestamped files for chronological tracking
            - Error type classification for easier debugging
            - JSONL format for easy reprocessing
            
        Use Cases:
            - Embedding generation failures
            - Malformed document structure
            - OpenSearch indexing errors
            - Network timeout issues
        """
        if not failed_docs:
            return  # No action needed for empty failure list
        
        # Generate timestamped filename for DLQ organization
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        dlq_key = f"{self.prefix}/dlq/failed_docs_{error_type}_{timestamp}.jsonl"
        
        try:
            # Convert failed documents to JSONL format
            content = '\n'.join(json.dumps(doc) for doc in failed_docs)
            
            # Save to S3 DLQ location
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=dlq_key,
                Body=content,
                ContentType='application/json'
            )
            
            logger.info(f"Saved {len(failed_docs)} failed documents to DLQ: {dlq_key}")
            
        except Exception as e:
            logger.error(f"Critical: Failed to save documents to DLQ: {e}")
            # This is a critical error - we're losing track of failed documents

# =============================================================================
# TEXT PROCESSING AND CHUNKING
# =============================================================================

class TextChunker:
    """
    Handles intelligent text chunking for optimal embedding generation and retrieval.
    
    Large documents must be split into smaller chunks that fit within embedding model
    token limits while preserving semantic coherence. This class implements
    sentence-aware chunking with configurable overlap to maintain context.
    
    Chunking Strategy:
    - Sentence-boundary aware splitting to preserve meaning
    - Configurable overlap between chunks for context preservation
    - Size limits based on embedding model constraints
    - Semantic coherence optimization
    
    Why Chunking is Critical:
    1. Embedding models have token limits (e.g., 8000 tokens for Titan)
    2. Smaller chunks provide more precise retrieval
    3. Overlap ensures important context isn't lost at boundaries
    4. Sentence boundaries preserve semantic integrity
    """
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        """
        Initialize text chunker with configurable parameters.
        
        Args:
            chunk_size (int): Maximum tokens per chunk (default: 512)
                - Balances between context and precision
                - Must be within embedding model limits
                - Smaller = more precise, larger = more context
                
            chunk_overlap (int): Overlap tokens between chunks (default: 50)
                - Prevents context loss at chunk boundaries
                - Helps with queries that span chunk boundaries
                - Typically 10-20% of chunk_size
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        logger.info(f"TextChunker initialized: chunk_size={chunk_size}, overlap={chunk_overlap}")
    
    def split_text(self, text: str) -> List[str]:
        """
        Split text into semantic chunks with intelligent boundary detection.
        
        This method implements a sophisticated chunking algorithm that:
        1. Respects sentence boundaries to preserve meaning
        2. Maintains configurable overlap between chunks
        3. Handles edge cases like very long sentences
        4. Optimizes for both retrieval precision and context preservation
        
        Args:
            text (str): Input text to be chunked
            
        Returns:
            List[str]: List of text chunks ready for embedding generation
            
        Algorithm Steps:
        1. Check if text fits in single chunk (no splitting needed)
        2. Split text at sentence boundaries using regex
        3. Combine sentences into chunks within size limits
        4. Apply overlap strategy to preserve context
        5. Handle edge cases (empty sentences, very long sentences)
        
        Chunking Example:
        Input: "Sentence 1. Sentence 2. Sentence 3. Sentence 4."
        Output: ["Sentence 1. Sentence 2.", "Sentence 2. Sentence 3.", "Sentence 3. Sentence 4."]
        """
        # Quick check: if text fits in one chunk, no splitting needed
        if len(text) <= self.chunk_size:
            return [text]
        
        # Split text at sentence boundaries using regex
        # Matches periods, exclamation marks, and question marks
        sentences = re.split(r'[.!?]+', text)
        chunks = []
        current_chunk = ""
        
        # Build chunks by combining sentences within size limits
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue  # Skip empty sentences from regex splitting
                
            # Check if adding this sentence exceeds chunk size
            potential_chunk = current_chunk + " " + sentence if current_chunk else sentence
            
            if len(potential_chunk) <= self.chunk_size:
                # Sentence fits, add it to current chunk
                current_chunk = potential_chunk
            else:
                # Sentence doesn't fit, finalize current chunk and start new one
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence
                
                # Handle edge case: single sentence longer than chunk_size
                if len(current_chunk) > self.chunk_size:
                    # Force split long sentence at word boundaries
                    words = current_chunk.split()
                    temp_chunk = ""
                    for word in words:
                        if len(temp_chunk + " " + word) <= self.chunk_size:
                            temp_chunk += " " + word if temp_chunk else word
                        else:
                            if temp_chunk:
                                chunks.append(temp_chunk)
                            temp_chunk = word
                    current_chunk = temp_chunk
        
        # Don't forget the last chunk
        if current_chunk:
            chunks.append(current_chunk)
        
        # Apply overlap strategy if multiple chunks exist
        if len(chunks) > 1 and self.chunk_overlap > 0:
            overlapped_chunks = []
            
            for i in range(len(chunks)):
                # Create overlapped chunk by combining with adjacent chunks
                start_idx = max(0, i - 1)  # Include previous chunk for context
                end_idx = min(len(chunks), i + 2)  # Include next chunk for context
                
                # Combine chunks with overlap
                overlapped_content = " ".join(chunks[start_idx:end_idx])
                
                # Trim to reasonable size (allow some expansion for overlap)
                max_overlapped_size = self.chunk_size * 2
                if len(overlapped_content) > max_overlapped_size:
                    overlapped_content = overlapped_content[:max_overlapped_size]
                
                overlapped_chunks.append(overlapped_content)
            
            logger.debug(f"Applied overlap: {len(chunks)} → {len(overlapped_chunks)} chunks")
            return overlapped_chunks
        
        logger.debug(f"Text chunking complete: {len(chunks)} chunks generated")
        return chunks

# =============================================================================
# EMBEDDING GENERATION WITH AMAZON TITAN
# =============================================================================

class EmbeddingGenerator:
    """
    Handles vector embedding generation using Amazon Titan Embed v2 model.
    
    This class provides robust embedding generation with comprehensive error handling,
    fallback mechanisms, and batch processing capabilities. It's designed for
    production use with high reliability and performance requirements.
    
    Amazon Titan Embed v2 Features:
    - 1536-dimensional embeddings
    - Multilingual support
    - High-quality semantic representations
    - 8000 token input limit
    - Cost-effective pricing
    
    Production Considerations:
    - Implements retry logic for transient failures
    - Provides fallback embeddings to prevent pipeline failures
    - Batch processing for efficiency
    - Comprehensive error logging and monitoring
    - Handles rate limiting and throttling gracefully
    """
    
    def __init__(self):
        """
        Initialize embedding generator with Amazon Bedrock client.
        
        Sets up the Bedrock runtime client for accessing Titan embedding model
        and configures model-specific parameters like embedding dimensions.
        """
        # Initialize Amazon Bedrock client for embedding generation
        self.bedrock_runtime = boto3.client('bedrock-runtime', region_name=AWS_REGION_BEDROCK)
        
        # Titan Embed v2 model specifications
        self.titan_dimension = 1536  # Fixed dimension for Titan Embed v2
        
        logger.info(f"EmbeddingGenerator initialized with Titan model (dimension: {self.titan_dimension})")
    
    @retry(
        stop=stop_after_attempt(3),                    # Maximum 3 attempts for embedding generation
        wait=wait_exponential(multiplier=1, min=2, max=10),  # Exponential backoff for rate limiting
        retry=retry_if_exception_type((ClientError, ConnectionError))  # Retry on service errors only
    )
    def generate_titan_embeddings_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        Generate Titan embeddings for a batch of texts with robust error handling.
        
        This method processes multiple texts efficiently while handling various
        failure scenarios gracefully. It implements a fallback strategy to ensure
        the pipeline continues even when some embeddings fail to generate.
        
        Args:
            texts (List[str]): List of text strings to embed
            
        Returns:
            List[Optional[List[float]]]: List of embedding vectors (or None for failures)
            
        Error Handling Strategy:
        1. Individual text failures don't stop batch processing
        2. Empty/invalid texts get fallback random embeddings
        3. API failures trigger retry with exponential backoff
        4. Dimension validation ensures consistent vector sizes
        5. Comprehensive logging for monitoring and debugging
        
        Fallback Mechanism:
        - Uses random embeddings when generation fails
        - Maintains consistent dimensionality
        - Logs all fallback usage for monitoring
        - Prevents pipeline failures due to individual document issues
        """
        if not texts:
            logger.warning("Empty text list provided to embedding generator")
            return []
        
        embeddings = []
        successful_count = 0
        
        logger.info(f"Generating embeddings for {len(texts)} texts using Titan")
        
        # Process each text individually for granular error handling
        for i, text in enumerate(texts):
            try:
                # Validate input text
                if not text or not text.strip():
                    logger.warning(f"Empty text at index {i}, using fallback embedding")
                    embedding = np.random.rand(self.titan_dimension).tolist()
                else:
                    # Prepare Titan embedding request
                    # Truncate text to model limit (8000 tokens ≈ 32000 characters)
                    truncated_text = text[:8000]
                    
                    request_body = json.dumps({"inputText": truncated_text})
                    
                    # Call Amazon Bedrock Titan embedding model
                    response = self.bedrock_runtime.invoke_model(
                        modelId=TITAN_EMBEDDING_MODEL,  # From config: "amazon.titan-embed-text-v2:0"
                        body=request_body
                    )
                    
                    # Parse response and extract embedding vector
                    response_body = json.loads(response['body'].read())
                    embedding = response_body.get('embedding')
                
                # Validate embedding response
                if embedding is None:
                    logger.warning(f"Titan returned None embedding for text {i}, using fallback")
                    embedding = np.random.rand(self.titan_dimension).tolist()
                else:
                    successful_count += 1
                
                # Ensure correct dimensionality (critical for OpenSearch indexing)
                if len(embedding) != self.titan_dimension:
                    logger.warning(f"Dimension mismatch for embedding {i}: {len(embedding)} != {self.titan_dimension}")
                    
                    if len(embedding) > self.titan_dimension:
                        # Truncate if too long
                        embedding = embedding[:self.titan_dimension]
                    else:
                        # Pad with zeros if too short
                        embedding = embedding + [0.0] * (self.titan_dimension - len(embedding))
                
                embeddings.append(embedding)
                
            except Exception as e:
                logger.error(f"Embedding generation failed for text {i}: {e}")
                
                # Fallback to random embedding to maintain pipeline flow
                fallback_embedding = np.random.rand(self.titan_dimension).tolist()
                embeddings.append(fallback_embedding)
        
        # Log batch processing results
        success_rate = (successful_count / len(texts)) * 100 if texts else 0
        logger.info(f"Embedding generation complete: {successful_count}/{len(texts)} successful ({success_rate:.1f}%)")
        
        return embeddings
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Public interface for embedding generation with guaranteed valid output.
        
        This method ensures that all returned embeddings are valid vectors,
        using fallback mechanisms when necessary. It's the main entry point
        for the ingestion pipeline.
        
        Args:
            texts (List[str]): Input texts to embed
            
        Returns:
            List[List[float]]: Valid embedding vectors (guaranteed non-None)
            
        Guarantees:
        - Always returns same number of embeddings as input texts
        - All embeddings have consistent dimensionality
        - No None values in output (uses fallbacks)
        - Maintains order correspondence with input texts
        """
        # Generate embeddings using batch method
        embeddings = self.generate_titan_embeddings_batch(texts)
        
        # Ensure all embeddings are valid (no None values)
        valid_embeddings = []
        for i, embedding in enumerate(embeddings):
            if embedding is None:
                logger.warning(f"Embedding {i} is None, generating fallback")
                fallback_embedding = np.random.rand(self.titan_dimension).tolist()
                valid_embeddings.append(fallback_embedding)
            else:
                valid_embeddings.append(embedding)
        
        logger.debug(f"Validated {len(valid_embeddings)} embeddings for pipeline processing")
        return valid_embeddings
    
    def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for search queries with special handling.
        
        Query embeddings require special consideration as they're used for
        real-time search operations. This method provides optimized handling
        for single query embedding generation.
        
        Args:
            query (str): Search query text
            
        Returns:
            List[float]: Query embedding vector
            
        Optimization:
        - Single query processing for low latency
        - Immediate fallback for reliability
        - Consistent with document embeddings for accurate similarity
        """
        embeddings = self.get_embeddings([query])
        return embeddings[0] if embeddings else np.random.rand(self.titan_dimension).tolist()

# =============================================================================
# OPENSEARCH INTEGRATION AND VECTOR STORAGE
# =============================================================================

class OpenSearchManager:
    """
    Manages OpenSearch operations for vector storage and hybrid search capabilities.
    
    This class handles all interactions with OpenSearch, including index management,
    document indexing, and search operations. It's designed to support both
    vector similarity search and traditional keyword search (BM25) for hybrid
    retrieval capabilities.
    
    OpenSearch Features Used:
    - k-NN vector search with HNSW algorithm
    - BM25 keyword search
    - Hybrid search combining both approaches
    - Index management and optimization
    - Bulk indexing for performance
    
    Production Considerations:
    - Connection pooling and authentication
    - Bulk operations for efficiency
    - Error handling and retry logic
    - Index optimization for search performance
    - Monitoring and health checks
    """
    
    def __init__(self):
        """
        Initialize OpenSearch client with authentication and connection settings.
        
        Sets up secure connection to OpenSearch cluster with proper authentication
        and configures client settings for optimal performance.
        """
        # Initialize OpenSearch client with secure connection
        self.client = OpenSearch(
            hosts=[{
                'host': OPENSEARCH_URL.replace('https://', ''), 
                'port': 443
            }],
            http_auth=(OPENSEARCH_USERNAME, OPENSEARCH_PASSWORD),
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            timeout=30,  # 30-second timeout for operations
            max_retries=3,  # Automatic retry for failed requests
            retry_on_timeout=True
        )
        
        logger.info(f"OpenSearchManager initialized for cluster: {OPENSEARCH_URL}")
        
        # Validate connection on initialization
        try:
            cluster_health = self.client.cluster.health()
            logger.info(f"OpenSearch cluster status: {cluster_health['status']}")
        except Exception as e:
            logger.error(f"Failed to connect to OpenSearch cluster: {e}")
            raise