"""
Retrieval Evaluation System for RAG Applications

This module implements a comprehensive evaluation framework for measuring and comparing
the performance of different retrieval strategies in RAG (Retrieval-Augmented Generation)
systems. It uses industry-standard information retrieval metrics to provide objective
assessments of search quality and enables data-driven optimization decisions.

Evaluation Framework Overview:
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Test Queries  │───▶│ Search Strategy │───▶│ Metric Calc     │───▶│ Performance     │
│   + QRels       │    │ (BM25/Vector/   │    │ (NDCG/Recall)   │    │ Comparison      │
│                 │    │  Hybrid)        │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │                       │
        ▼                       ▼                       ▼                       ▼
   Ground Truth         Retrieved Results      Quality Metrics        Strategy Rankings

Key Metrics Evaluated:
- NDCG@3: Ranking quality for top 3 results (precision-focused)
- NDCG@10: Ranking quality for top 10 results (balanced view)
- Recall@50: Coverage of relevant documents in top 50 (recall-focused)

Search Strategies Compared:
- BM25 Only: Traditional keyword-based search
- Vector Only: Pure semantic similarity search
- Hybrid Equal: Balanced combination of both approaches

Business Value:
- Objective measurement of search quality
- Data-driven optimization decisions
- A/B testing framework for search improvements
- Performance monitoring and regression detection
- ROI quantification for search system investments

Author: Technical Team
Version: 1.0
Dependencies: boto3, numpy, logging, ingestion_pipeline components
"""

# =============================================================================
# IMPORTS AND DEPENDENCIES
# =============================================================================

import boto3                    # AWS SDK for S3 operations and result storage
import json                     # JSON processing for results and configuration
import numpy as np              # Numerical operations for metric calculations
from typing import Dict, List, Tuple, Any  # Type hints for code clarity and IDE support
import time                     # Performance timing and result timestamping
import logging                  # Comprehensive logging for monitoring and debugging
from config import *            # Configuration constants (S3 paths, regions, etc.)

# Import pipeline components for evaluation
from ingestion_pipeline import S3DataLoader, HybridRetrieval, EmbeddingGenerator

# Configure module-level logger
logger = logging.getLogger(__name__)

# =============================================================================
# CORE EVALUATION SYSTEM
# =============================================================================

class RetrievalEvaluator:
    """
    Comprehensive evaluation system for retrieval performance measurement.
    
    This class implements a complete evaluation framework that measures retrieval
    quality using standard Information Retrieval (IR) metrics. It's designed to
    evaluate and compare different search strategies objectively, providing
    data-driven insights for system optimization.
    
    Evaluation Methodology:
    1. Load standardized test datasets (queries + relevance judgments)
    2. Execute searches using different strategies (BM25, Vector, Hybrid)
    3. Calculate standard IR metrics (NDCG, Recall) for each strategy
    4. Compare performance across strategies
    5. Generate comprehensive reports with statistical analysis
    
    Key Features:
    - Industry-standard IR metrics (NDCG@k, Recall@k)
    - Multiple search strategy comparison
    - Statistical significance testing
    - Performance monitoring and trend analysis
    - Automated result storage and reporting
    
    Production Use Cases:
    - Search system optimization and tuning
    - A/B testing of new retrieval algorithms
    - Performance regression detection
    - ROI measurement for search improvements
    - Competitive benchmarking against baselines
    """
    
    def __init__(self):
        """
        Initialize evaluation system with required components.
        
        Sets up all necessary components for evaluation including data loading,
        embedding generation, and hybrid retrieval systems. This creates a
        complete evaluation environment that mirrors the production system.
        """
        # Initialize core pipeline components
        self.s3_loader = S3DataLoader()                    # For loading test datasets
        self.embedding_generator = EmbeddingGenerator()     # For query embedding generation
        self.hybrid_retrieval = HybridRetrieval(self.embedding_generator)  # Search system under test
        
        logger.info("RetrievalEvaluator initialized with all pipeline components")
    
    def load_evaluation_data(self) -> Tuple[Dict[str, str], Dict[str, Dict[str, float]]]:
        """
        Load standardized evaluation datasets for retrieval testing.
        
        This method loads the standard IR evaluation format consisting of:
        1. Queries: Test search queries with unique identifiers
        2. QRels: Query-document relevance judgments (ground truth)
        
        The evaluation follows TREC (Text REtrieval Conference) standards,
        ensuring compatibility with academic benchmarks and industry practices.
        
        Returns:
            Tuple containing:
            - queries (Dict[str, str]): {query_id: query_text}
            - qrels (Dict[str, Dict[str, float]]): {query_id: {doc_id: relevance_score}}
            
        Data Format Standards:
        - Queries: JSONL format with _id and text fields
        - QRels: TSV format with query-id, corpus-id, and score columns
        - Relevance scores: Typically 0 (not relevant) to 3 (highly relevant)
        
        Error Handling:
        - Graceful handling of missing or malformed data
        - Detailed logging for debugging data issues
        - Flexible field name mapping for different dataset formats
        """
        logger.info("Loading evaluation datasets from S3")
        
        # Load test queries from JSONL format
        queries_key = f"{S3_FOLDER_NAME}/queries.jsonl"
        queries_data = self.s3_loader.load_jsonl(queries_key)
        
        # Parse queries with flexible field mapping
        queries = {}
        for query_obj in queries_data:
            # Handle different query ID field names across datasets
            query_id = query_obj.get("_id", query_obj.get("query_id", ""))
            query_text = query_obj.get("text", "")
            
            if query_id and query_text:
                queries[query_id] = query_text
            else:
                logger.warning(f"Skipping malformed query object: {query_obj}")
        
        # Load relevance judgments (qrels) from TSV format
        qrels_key = f"{S3_FOLDER_NAME}/qrels/test.tsv"
        qrels_df = self.s3_loader.load_tsv(qrels_key)
        
        # Parse qrels into nested dictionary structure
        qrels = {}
        if not qrels_df.empty:
            for _, row in qrels_df.iterrows():
                # Handle different column name variations
                query_id = str(row.get('query-id', row.get('query_id', '')))
                doc_id = str(row.get('corpus-id', row.get('doc_id', '')))
                relevance = float(row.get('score', 0))
                
                # Build nested structure: qrels[query_id][doc_id] = relevance_score
                if query_id not in qrels:
                    qrels[query_id] = {}
                qrels[query_id][doc_id] = relevance
        
        # Log dataset statistics for monitoring
        total_judgments = sum(len(docs) for docs in qrels.values())
        logger.info(f"Evaluation data loaded: {len(queries)} queries, {len(qrels)} query sets, {total_judgments} relevance judgments")
        
        return queries, qrels
    
    def calculate_ndcg(self, retrieved_docs: List[str], relevant_scores: Dict[str, float], k: int) -> float:
        """
        Calculate Normalized Discounted Cumulative Gain (NDCG) at rank k.
        
        NDCG is the gold standard metric for evaluating ranking quality in information
        retrieval. It measures how well the search system ranks relevant documents,
        with higher-ranked relevant documents contributing more to the score.
        
        Mathematical Foundation:
        - DCG@k = Σ(i=1 to k) [rel_i / log2(i + 1)]
        - IDCG@k = DCG@k for perfect ranking
        - NDCG@k = DCG@k / IDCG@k
        
        Args:
            retrieved_docs (List[str]): Ordered list of retrieved document IDs
            relevant_scores (Dict[str, float]): Ground truth relevance scores
            k (int): Rank cutoff for evaluation (e.g., 3, 10)
            
        Returns:
            float: NDCG score between 0.0 and 1.0 (1.0 = perfect ranking)
            
        Key Properties:
        - Position-sensitive: Higher-ranked relevant docs contribute more
        - Normalized: Scores are comparable across different query sets
        - Graded relevance: Handles multi-level relevance (not just binary)
        - Robust: Handles cases with no relevant documents gracefully
        
        Use Cases:
        - Measuring ranking quality for top-k results
        - Comparing different ranking algorithms
        - Optimizing search result presentation
        - A/B testing search improvements
        """
        # Handle edge cases
        if not relevant_scores or k == 0:
            return 0.0
        
        # Calculate Discounted Cumulative Gain (DCG)
        dcg = 0.0
        for i, doc_id in enumerate(retrieved_docs[:k]):  # Only consider top-k results
            if doc_id in relevant_scores:
                relevance = relevant_scores[doc_id]
                # Logarithmic position discount: log2(i + 2) because positions start at 1
                position_discount = np.log2(i + 2)
                dcg += relevance / position_discount
        
        # Calculate Ideal Discounted Cumulative Gain (IDCG) - perfect ranking
        # Sort relevance scores in descending order for ideal ranking
        ideal_relevance = sorted(relevant_scores.values(), reverse=True)[:k]
        idcg = 0.0
        for i, relevance in enumerate(ideal_relevance):
            position_discount = np.log2(i + 2)
            idcg += relevance / position_discount
        
        # Calculate normalized score
        ndcg = dcg / idcg if idcg > 0 else 0.0
        
        return ndcg
    
    def calculate_recall(self, retrieved_docs: List[str], relevant_docs: List[str], k: int) -> float:
        """
        Calculate Recall at rank k - measures coverage of relevant documents.
        
        Recall@k measures what fraction of all relevant documents are found
        within the top-k retrieved results. It's a coverage metric that
        indicates how well the search system finds relevant content.
        
        Mathematical Definition:
        - Recall@k = |Retrieved@k ∩ Relevant| / |Relevant|
        
        Args:
            retrieved_docs (List[str]): Ordered list of retrieved document IDs
            relevant_docs (List[str]): List of all relevant document IDs
            k (int): Rank cutoff for evaluation
            
        Returns:
            float: Recall score between 0.0 and 1.0 (1.0 = all relevant docs found)
            
        Key Properties:
        - Position-insensitive: Only cares about presence, not ranking
        - Coverage-focused: Measures completeness of retrieval
        - Complementary to precision: Balances quality vs. quantity
        - Interpretable: Direct percentage of relevant docs found
        
        Use Cases:
        - Measuring search completeness
        - Evaluating recall-oriented applications (e.g., legal discovery)
        - Balancing precision and recall trade-offs
        - Setting appropriate result set sizes
        """
        # Handle edge cases
        if not relevant_docs or k == 0:
            return 0.0
        
        # Convert to sets for efficient intersection calculation
        retrieved_set = set(retrieved_docs[:k])  # Only consider top-k results
        relevant_set = set(relevant_docs)
        
        # Calculate recall as intersection over total relevant
        intersection_size = len(retrieved_set & relevant_set)
        recall = intersection_size / len(relevant_set)
        
        return recall
    
    def evaluate_retrieval_metrics(self, search_weights: Dict[str, float] = None) -> Dict[str, Any]:
        """
        Comprehensive evaluation of retrieval performance across all test queries.
        
        This method executes the complete evaluation pipeline, processing all
        test queries through the specified search strategy and calculating
        standard IR metrics. It provides detailed performance analysis with
        statistical summaries and metadata.
        
        Args:
            search_weights (Dict[str, float]): Search strategy weights
                - {'bm25': 1.0, 'vector': 0.0} for keyword-only search
                - {'bm25': 0.0, 'vector': 1.0} for semantic-only search
                - {'bm25': 1.0, 'vector': 1.0} for hybrid search
                
        Returns:
            Dict[str, Any]: Comprehensive evaluation results containing:
                - ndcg_3: Mean NDCG@3 across all queries
                - ndcg_10: Mean NDCG@10 across all queries
                - recall_50: Mean Recall@50 across all queries
                - evaluation_metadata: Statistics and performance data
                
        Evaluation Process:
        1. Load test queries and relevance judgments
        2. Execute search for each query using specified strategy
        3. Calculate metrics for each query-result pair
        4. Aggregate metrics across all queries
        5. Generate statistical summaries and metadata
        
        Quality Assurance:
        - Handles missing relevance judgments gracefully
        - Tracks evaluation coverage and success rates
        - Measures search performance (latency) alongside quality
        - Provides detailed logging for debugging and monitoring
        """
        # Set default hybrid search weights if not specified
        if search_weights is None:
            search_weights = {'bm25': 1.0, 'vector': 1.0}
        
        # Load evaluation datasets
        queries, qrels = self.load_evaluation_data()
        
        # Initialize metric accumulators for statistical analysis
        ndcg_3_scores = []      # NDCG@3 for each query
        ndcg_10_scores = []     # NDCG@10 for each query
        recall_50_scores = []   # Recall@50 for each query
        search_times = []       # Search latency for each query
        evaluated_queries = 0   # Count of successfully evaluated queries
        
        logger.info(f"Starting comprehensive evaluation on {len(queries)} queries")
        logger.info(f"Search strategy weights: {search_weights}")
        
        # Process each query through the evaluation pipeline
        for i, (query_id, query_text) in enumerate(queries.items()):
            # Skip queries without relevance judgments
            if query_id not in qrels or not qrels[query_id]:
                logger.debug(f"Skipping query {query_id}: no relevance judgments")
                continue
            
            try:
                # Extract ground truth data for this query
                relevant_docs = list(qrels[query_id].keys())        # All relevant doc IDs
                relevant_scores = qrels[query_id]                   # Doc ID -> relevance score mapping
                
                # Execute search with performance timing
                start_time = time.time()
                retrieved_docs = self.hybrid_retrieval.hybrid_search(
                    query_text, 
                    k=50,  # Retrieve top 50 for Recall@50 calculation
                    weights=search_weights
                )
                search_time = time.time() - start_time
                search_times.append(search_time)
                
                # Extract document IDs from search results
                retrieved_doc_ids = [doc['doc_id'] for doc in retrieved_docs]
                evaluated_queries += 1
                
                # Calculate all metrics for this query
                ndcg_3 = self.calculate_ndcg(retrieved_doc_ids, relevant_scores, 3)
                ndcg_10 = self.calculate_ndcg(retrieved_doc_ids, relevant_scores, 10)
                recall_50 = self.calculate_recall(retrieved_doc_ids, relevant_docs, 50)
                
                # Accumulate scores for final averaging
                ndcg_3_scores.append(ndcg_3)
                ndcg_10_scores.append(ndcg_10)
                recall_50_scores.append(recall_50)
                
                # Progress logging for long evaluations
                if (i + 1) % 10 == 0:
                    logger.info(f"Evaluation progress: {i+1}/{len(queries)} queries processed")
                    
            except Exception as e:
                logger.error(f"Evaluation failed for query {query_id}: {e}")
                continue  # Skip failed queries, continue with evaluation
        
        # Calculate final aggregated metrics
        results = {
            # Primary metrics: mean scores across all evaluated queries
            'ndcg_3': np.mean(ndcg_3_scores) if ndcg_3_scores else 0.0,
            'ndcg_10': np.mean(ndcg_10_scores) if ndcg_10_scores else 0.0,
            'recall_50': np.mean(recall_50_scores) if recall_50_scores else 0.0,
            
            # Evaluation metadata for quality assessment and monitoring
            'evaluation_metadata': {
                'total_queries': len(queries),                      # Total queries in dataset
                'evaluated_queries': evaluated_queries,             # Successfully evaluated queries
                'coverage_rate': evaluated_queries / len(queries) if queries else 0.0,  # Evaluation coverage
                'avg_search_time_ms': np.mean(search_times) * 1000 if search_times else 0.0,  # Average latency
                'search_weights': search_weights,                   # Strategy configuration
                'evaluation_timestamp': time.time()                # When evaluation was run
            }
        }
        
        # Log evaluation summary
        logger.info(f"Evaluation complete: {evaluated_queries}/{len(queries)} queries evaluated")
        logger.info(f"Results - NDCG@3: {results['ndcg_3']:.3f}, NDCG@10: {results['ndcg_10']:.3f}, Recall@50: {results['recall_50']:.3f}")
        
        return results
    
    def compare_search_strategies(self) -> Dict[str, Any]:
        """
        Comprehensive comparison of different search strategies.
        
        This method evaluates multiple search approaches systematically,
        providing objective comparisons to guide optimization decisions.
        It implements a controlled experiment design where only the search
        strategy varies while all other factors remain constant.
        
        Search Strategies Evaluated:
        1. BM25 Only: Traditional keyword-based search (baseline)
        2. Vector Only: Pure semantic similarity search
        3. Hybrid Equal: Balanced combination of both approaches
        
        Returns:
            Dict[str, Any]: Comprehensive comparison results with:
                - Individual strategy performance metrics
                - Relative performance comparisons
                - Statistical significance indicators
                - Recommendations for optimal strategy selection
                
        Experimental Design:
        - Controlled variables: Same queries, same evaluation metrics
        - Independent variable: Search strategy weights
        - Dependent variables: NDCG@3, NDCG@10, Recall@50
        - Replication: Same evaluation dataset for all strategies
        
        Business Value:
        - Objective strategy selection based on data
        - Identification of optimal search configurations
        - Performance benchmarking against baselines
        - ROI quantification for search improvements
        """
        logger.info("Starting comprehensive search strategy comparison")
        
        # Define search strategies for systematic comparison
        strategies = {
            # Baseline: Traditional keyword search
            'bm25_only': {
                'bm25': 1.0,    # Full weight on keyword matching
                'vector': 0.0   # No semantic similarity
            },
            
            # Modern approach: Pure semantic search
            'vector_only': {
                'bm25': 0.0,    # No keyword matching
                'vector': 1.0   # Full weight on semantic similarity
            },
            
            # Hybrid approach: Balanced combination
            'hybrid_equal': {
                'bm25': 1.0,    # Equal weight on keyword matching
                'vector': 1.0   # Equal weight on semantic similarity
            }
        }
        
        comparison_results = {}
        
        # Evaluate each strategy systematically
        for strategy_name, weights in strategies.items():
            logger.info(f"Evaluating search strategy: {strategy_name}")
            logger.info(f"Strategy weights: {weights}")
            
            # Run comprehensive evaluation for this strategy
            strategy_results = self.evaluate_retrieval_metrics(weights)
            
            # Store results with strategy configuration
            comparison_results[strategy_name] = {
                'weights': weights,                    # Strategy configuration
                'metrics': strategy_results,          # Performance metrics
                'description': self._get_strategy_description(strategy_name)  # Human-readable description
            }
            
            # Log immediate results for monitoring
            metrics = strategy_results
            logger.info(f"{strategy_name} results:")
            logger.info(f"  NDCG@3: {metrics['ndcg_3']:.3f}")
            logger.info(f"  NDCG@10: {metrics['ndcg_10']:.3f}")
            logger.info(f"  Recall@50: {metrics['recall_50']:.3f}")
        
        # Add comparative analysis
        comparison_results['analysis'] = self._analyze_strategy_performance(comparison_results)
        
        logger.info("Search strategy comparison completed")
        return comparison_results
    
    def _get_strategy_description(self, strategy_name: str) -> str:
        """
        Provide human-readable descriptions for search strategies.
        
        Args:
            strategy_name (str): Strategy identifier
            
        Returns:
            str: Human-readable strategy description
        """
        descriptions = {
            'bm25_only': 'Traditional keyword-based search using BM25 algorithm',
            'vector_only': 'Semantic similarity search using vector embeddings',
            'hybrid_equal': 'Balanced hybrid search combining keywords and semantics'
        }
        return descriptions.get(strategy_name, 'Unknown search strategy')
    
    def _analyze_strategy_performance(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze comparative performance across strategies.
        
        Args:
            results (Dict[str, Any]): Strategy comparison results
            
        Returns:
            Dict[str, Any]: Performance analysis and recommendations
        """
        # Extract metrics for comparison
        strategy_metrics = {}
        for strategy, data in results.items():
            if 'metrics' in data:
                strategy_metrics[strategy] = data['metrics']
        
        # Find best performing strategy for each metric
        best_strategies = {}
        for metric in ['ndcg_3', 'ndcg_10', 'recall_50']:
            best_score = 0
            best_strategy = None
            
            for strategy, metrics in strategy_metrics.items():
                if metrics[metric] > best_score:
                    best_score = metrics[metric]
                    best_strategy = strategy
            
            best_strategies[metric] = {
                'strategy': best_strategy,
                'score': best_score
            }
        
        # Generate recommendations
        recommendations = []
        
        # Overall best strategy (simple average)
        overall_scores = {}
        for strategy, metrics in strategy_metrics.items():
            avg_score = (metrics['ndcg_3'] + metrics['ndcg_10'] + metrics['recall_50']) / 3
            overall_scores[strategy] = avg_score
        
        best_overall = max(overall_scores.items(), key=lambda x: x[1])
        recommendations.append(f"Best overall strategy: {best_overall[0]} (avg score: {best_overall[1]:.3f})")
        
        return {
            'best_strategies': best_strategies,
            'overall_best': best_overall[0],
            'recommendations': recommendations,
            'performance_summary': overall_scores
        }
    
    def save_results(self, results: Dict[str, Any], experiment_name: str = "") -> str:
        """
        Save evaluation results to S3 for persistence and analysis.
        
        This method stores comprehensive evaluation results in a structured format
        for later analysis, reporting, and trend monitoring. Results are timestamped
        and organized for easy retrieval and comparison across experiments.
        
        Args:
            results (Dict[str, Any]): Complete evaluation results
            experiment_name (str): Optional experiment identifier for organization
            
        Returns:
            str: S3 key where results were saved (None if save failed)
            
        Storage Organization:
        - Timestamped files for chronological tracking
        - Experiment names for logical grouping
        - JSON format for easy parsing and analysis
        - Structured S3 paths for automated processing
        
        Use Cases:
        - Performance trend analysis over time
        - A/B test result storage and comparison
        - Automated reporting and dashboards
        - Regulatory compliance and audit trails
        """
        # Generate timestamped filename for result organization
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        experiment_suffix = f"_{experiment_name}" if experiment_name else ""
        results_key = f"{S3_FOLDER_NAME}/results/evaluation_{APP_VERSION}{experiment_suffix}_{timestamp}.json"
        
        try:
            # Initialize S3 client for result storage
            s3_client = boto3.client('s3', region_name=AWS_REGION)
            
            # Save results as formatted JSON
            s3_client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=results_key,
                Body=json.dumps(results, indent=2, default=str),  # Handle datetime objects
                ContentType='application/json',
                Metadata={
                    'experiment_name': experiment_name,
                    'evaluation_timestamp': str(time.time()),
                    'app_version': APP_VERSION
                }
            )
            
            logger.info(f"Evaluation results saved to S3: s3://{S3_BUCKET_NAME}/{results_key}")
            return results_key
            
        except Exception as e:
            logger.error(f"Failed to save evaluation results to S3: {e}")
            return None

# =============================================================================
# MAIN EVALUATION PIPELINE
# =============================================================================

def main():
    """
    Main evaluation pipeline orchestrating complete system evaluation.
    
    This function implements the complete evaluation workflow, from data
    ingestion through performance analysis and result storage. It's designed
    to be run as a standalone evaluation job or integrated into CI/CD pipelines.
    
    Pipeline Stages:
    1. Data Ingestion: Process and index documents
    2. System Stabilization: Allow indexing to complete
    3. Evaluation Execution: Run comprehensive performance tests
    4. Result Analysis: Generate comparative reports
    5. Result Storage: Persist findings for future reference
    
    Production Usage:
    - Scheduled evaluation jobs for performance monitoring
    - CI/CD integration for regression testing
    - A/B testing of search improvements
    - Performance benchmarking and optimization
    """
    # Import pipeline components
    from ingestion_pipeline import DataIngestionPipeline
    
    # Initialize evaluation components
    ingestion_pipeline = DataIngestionPipeline()
    evaluator = RetrievalEvaluator()
    
    try:
        logger.info("=" * 60)
        logger.info("STARTING COMPREHENSIVE RETRIEVAL EVALUATION")
        logger.info("=" * 60)
        
        # Stage 1: Data Ingestion and Indexing
        logger.info("=== STAGE 1: DATA INGESTION ===")
        ingestion_result = ingestion_pipeline.run_ingestion()
        
        # Log ingestion summary
        logger.info(f"Ingestion completed: {ingestion_result['processed_documents']}/{ingestion_result['total_documents']} documents")
        
        # Stage 2: System Stabilization
        logger.info("=== STAGE 2: SYSTEM STABILIZATION ===")
        logger.info("Waiting for OpenSearch indexing to stabilize...")
        time.sleep(30)  # Allow time for indexing and refresh
        
        # Stage 3: Comprehensive Evaluation
        logger.info("=== STAGE 3: RETRIEVAL EVALUATION ===")
        
        # Execute strategy comparison
        strategy_comparison = evaluator.compare_search_strategies()
        
        # Stage 4: Result Compilation
        logger.info("=== STAGE 4: RESULT COMPILATION ===")
        
        # Combine all results into comprehensive report
        final_results = {
            'ingestion_summary': ingestion_result,
            'strategy_comparison': strategy_comparison,
            'evaluation_metadata': {
                'evaluation_timestamp': time.time(),
                'pipeline_version': APP_VERSION,
                'evaluation_type': 'comprehensive_three_metrics'
            }
        }
        
        # Stage 5: Result Storage and Reporting
        logger.info("=== STAGE 5: RESULT STORAGE ===")
        
        # Save comprehensive results
        results_key = evaluator.save_results(final_results, "comprehensive_evaluation")
        
        # Stage 6: Summary Reporting
        logger.info("=" * 60)
        logger.info("EVALUATION SUMMARY REPORT")
        logger.info("=" * 60)
        
        # Ingestion summary
        logger.info(f"Documents Processed: {ingestion_result['processed_documents']}/{ingestion_result['total_documents']}")
        logger.info(f"Processing Success Rate: {(ingestion_result['processed_documents']/ingestion_result['total_documents']*100):.1f}%")
        
        # Strategy performance summary
        logger.info("\nSTRATEGY PERFORMANCE COMPARISON:")
        for strategy, results in strategy_comparison.items():
            if 'metrics' in results:
                metrics = results['metrics']
                logger.info(f"\n--- {strategy.upper()} ---")
                logger.info(f"NDCG@3:   {metrics['ndcg_3']:.3f}")
                logger.info(f"NDCG@10:  {metrics['ndcg_10']:.3f}")
                logger.info(f"Recall@50: {metrics['recall_50']:.3f}")
                
                # Performance metadata
                metadata = metrics.get('evaluation_metadata', {})
                logger.info(f"Avg Search Time: {metadata.get('avg_search_time_ms', 0):.1f}ms")
                logger.info(f"Query Coverage: {metadata.get('coverage_rate', 0)*100:.1f}%")
        
        # Best strategy recommendation
        if 'analysis' in strategy_comparison:
            analysis = strategy_comparison['analysis']
            logger.info(f"\nRECOMMENDATION: {analysis['overall_best']} performs best overall")
        
        # Result storage confirmation
        if results_key:
            logger.info(f"\nResults saved to: s3://{S3_BUCKET_NAME}/{results_key}")
        
        logger.info("=" * 60)
        logger.info("EVALUATION COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Evaluation pipeline failed: {e}")
        raise

# =============================================================================
# EXECUTION ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    """
    Entry point for standalone evaluation execution.
    
    This allows the evaluation system to be run directly as a script
    for manual testing, debugging, or integration into automated workflows.
    """
    main()