"""
Content Quality Evaluation Module

This module provides comprehensive content analysis capabilities for generated text,
including readability assessment, sentiment analysis, bias detection, and similarity
scoring. It serves as the quality assurance layer for the content generation pipeline.

Key Features:
- Readability scoring using Flesch metrics
- Sentiment analysis with VADER sentiment analyzer
- Bias detection for inclusive content creation
- ROUGE scoring for content similarity comparison
- Extensible framework for additional quality metrics

Dependencies:
- textstat: For readability calculations
- vaderSentiment: For sentiment analysis
- rouge-score: For text similarity metrics

Author: Technical Team
Version: 1.0
Usage: Import functions to analyze generated content quality in real-time
"""

# =============================================================================
# IMPORTS AND DEPENDENCIES
# =============================================================================

from textstat import flesch_reading_ease, flesch_kincaid_grade  # Readability metrics
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer  # Sentiment analysis
from rouge_score import rouge_scorer  # Text similarity scoring

# =============================================================================
# GLOBAL ANALYZERS AND CONFIGURATION
# =============================================================================

# Initialize sentiment analyzer for consistent scoring across all content
# VADER (Valence Aware Dictionary and sEntiment Reasoner) is optimized for social media text
analyzer = SentimentIntensityAnalyzer()

# Configure ROUGE scorer for content similarity analysis
# ROUGE-1: Unigram overlap, ROUGE-L: Longest common subsequence
scorer = rouge_scorer.RougeScorer(['rouge1', 'rougeL'], use_stemmer=True)

# Bias Detection Configuration
# Define terms that may indicate gender bias in content
# Note: This is a basic implementation - expand based on comprehensive bias guidelines
GENDERED_TERMS = [
    "he's", "she's", "guys", "ladies", "gentlemen"
]  # Expandable list for comprehensive bias detection

# =============================================================================
# READABILITY ANALYSIS FUNCTIONS
# =============================================================================

def readability_score(text: str) -> dict:
    """
    Calculate comprehensive readability metrics for content accessibility assessment.
    
    Uses established readability formulas to determine how easily content can be
    understood by target audiences. Higher Flesch Reading Ease scores indicate
    easier readability, while Flesch-Kincaid Grade Level corresponds to US
    educational grade levels.
    
    Args:
        text (str): Content text to analyze for readability
    
    Returns:
        dict: Readability metrics containing:
            - flesch_reading_ease (float): Score 0-100, higher = more readable
                * 90-100: Very Easy (5th grade level)
                * 80-89: Easy (6th grade level)
                * 70-79: Fairly Easy (7th grade level)
                * 60-69: Standard (8th-9th grade level)
                * 50-59: Fairly Difficult (10th-12th grade level)
                * 30-49: Difficult (college level)
                * 0-29: Very Difficult (graduate level)
            - flesch_kincaid_grade (float): US grade level equivalent
    
    Example:
        >>> readability_score("This is simple text.")
        {'flesch_reading_ease': 85.2, 'flesch_kincaid_grade': 3.1}
    """
    return {
        "flesch_reading_ease": flesch_reading_ease(text),
        "flesch_kincaid_grade": flesch_kincaid_grade(text)
    }

# =============================================================================
# SENTIMENT ANALYSIS FUNCTIONS
# =============================================================================

def sentiment_score(text: str) -> dict:
    """
    Perform comprehensive sentiment analysis using VADER sentiment analyzer.
    
    VADER is specifically designed for social media text and handles:
    - Punctuation emphasis (e.g., "!!!")
    - Capitalization for emphasis
    - Emoticons and emojis
    - Slang and informal language
    - Negation handling
    
    Args:
        text (str): Content text to analyze for sentiment
    
    Returns:
        dict: Sentiment scores containing:
            - neg (float): Negative sentiment ratio (0.0 to 1.0)
            - neu (float): Neutral sentiment ratio (0.0 to 1.0)
            - pos (float): Positive sentiment ratio (0.0 to 1.0)
            - compound (float): Overall sentiment score (-1.0 to 1.0)
                * >= 0.05: Positive sentiment
                * <= -0.05: Negative sentiment
                * Between -0.05 and 0.05: Neutral sentiment
    
    Example:
        >>> sentiment_score("This product is amazing!")
        {'neg': 0.0, 'neu': 0.294, 'pos': 0.706, 'compound': 0.6249}
    """
    # Get polarity scores from VADER analyzer
    vs = analyzer.polarity_scores(text)
    return vs  # Returns dictionary with neg/neu/pos/compound scores

# =============================================================================
# BIAS DETECTION FUNCTIONS
# =============================================================================

def bias_checks(text: str) -> dict:
    """
    Detect potential bias in content through pattern matching and term analysis.
    
    This function identifies potentially biased language that may exclude or
    alienate certain audience segments. Currently focuses on gender bias
    detection but can be extended for other bias types.
    
    Args:
        text (str): Content text to analyze for bias indicators
    
    Returns:
        dict: Bias analysis results containing:
            - gendered_terms (list): List of detected gendered terms
            - flagged (bool): Whether bias indicators were found
    
    Note:
        This is a basic implementation. For production use, consider:
        - More comprehensive bias term databases
        - Context-aware bias detection
        - Cultural sensitivity analysis
        - Accessibility language checks
    
    Example:
        >>> bias_checks("Hey guys, check out this product!")
        {'gendered_terms': ['guys'], 'flagged': True}
    """
    # Case-insensitive search for gendered terms in content
    found = [w for w in GENDERED_TERMS if w.lower() in text.lower()]
    
    return {
        "gendered_terms": found, 
        "flagged": len(found) > 0
    }

# =============================================================================
# CONTENT SIMILARITY FUNCTIONS
# =============================================================================

def rouge_scores(candidate: str, reference: str) -> dict:
    """
    Calculate ROUGE (Recall-Oriented Understudy for Gisting Evaluation) scores
    to measure content similarity between generated text and reference content.
    
    ROUGE metrics are commonly used in text summarization and generation tasks
    to evaluate how well generated content captures the essence of reference text.
    
    Args:
        candidate (str): Generated content to evaluate
        reference (str): Reference content for comparison
    
    Returns:
        dict: ROUGE scores containing:
            - rouge1: Unigram (single word) overlap metrics
                * precision: Fraction of candidate unigrams in reference
                * recall: Fraction of reference unigrams in candidate  
                * fmeasure: Harmonic mean of precision and recall
            - rougeL: Longest Common Subsequence (LCS) metrics
                * precision: LCS length / candidate length
                * recall: LCS length / reference length
                * fmeasure: Harmonic mean of precision and recall
        
        Empty dict if no reference text provided
    
    Example:
        >>> rouge_scores("The cat sat", "The cat sat on the mat")
        {
            'rouge1': Score(precision=1.0, recall=0.6, fmeasure=0.75),
            'rougeL': Score(precision=1.0, recall=0.6, fmeasure=0.75)
        }
    
    Use Cases:
        - Content variation analysis
        - Template adherence checking
        - Plagiarism detection
        - Content consistency measurement
    """
    # Validate reference text availability
    if not reference:
        return {}
    
    # Calculate ROUGE scores using configured scorer
    return scorer.score(reference, candidate)

# =============================================================================
# FUTURE ENHANCEMENT OPPORTUNITIES
# =============================================================================

"""
Potential additions for comprehensive content evaluation:

1. Advanced Bias Detection:
   - Racial/ethnic bias terms
   - Age-related bias
   - Socioeconomic bias
   - Disability-related language
   - Religious bias detection

2. Content Quality Metrics:
   - Coherence scoring
   - Factual accuracy checking
   - Brand voice consistency
   - Tone appropriateness
   - Call-to-action effectiveness

3. SEO and Marketing Metrics:
   - Keyword density analysis
   - Meta description optimization
   - Social media engagement prediction
   - Conversion potential scoring

4. Multilingual Support:
   - Language detection
   - Cross-language sentiment analysis
   - Cultural appropriateness checking
   - Localization quality assessment

5. Real-time Feedback:
   - Streaming analysis for long content
   - Progressive quality scoring
   - Dynamic threshold adjustment
   - Contextual recommendations
"""