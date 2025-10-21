"""
Content Safety and Guardrails Module

This module implements comprehensive content safety mechanisms and guardrails for
AI-generated content. It provides moderation capabilities, content filtering, and
automated content rewriting to ensure compliance with safety policies and brand guidelines.

Key Features:
- Real-time content moderation using OpenAI's moderation API
- Automated content rewriting for policy violations
- Extensible framework for custom safety rules
- Integration-ready for FloTorch guardrails system
- Comprehensive error handling and fallback mechanisms

Safety Categories Covered:
- Hate speech and harassment
- Self-harm content
- Sexual content
- Violence and graphic content
- Illegal activities
- Spam and misleading information

Dependencies:
- openai: For moderation API and content rewriting
- os: For environment variable management

Author: Technical Team
Version: 1.0
Usage: Import functions to add safety layers to content generation pipeline
"""

# =============================================================================
# IMPORTS AND DEPENDENCIES
# =============================================================================

import os      # Environment variable access for secure API key management
import openai  # OpenAI API client for moderation and rewriting services

# =============================================================================
# SECURITY AND API CONFIGURATION
# =============================================================================

# Secure API Key Management
# Retrieve OpenAI API key from environment variables for security
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_KEY

# Validate API key presence for critical safety functionality
if not OPENAI_KEY:
    print("Warning: OPENAI_API_KEY not found. Moderation features will be limited.")

# =============================================================================
# CONTENT MODERATION FUNCTIONS
# =============================================================================

def moderate_text(text: str) -> dict:
    """
    Perform comprehensive content moderation using OpenAI's moderation endpoint.
    
    This function analyzes text content for policy violations across multiple
    safety categories. It provides detailed flagging information and confidence
    scores for each category, enabling fine-grained content filtering decisions.
    
    Args:
        text (str): Content text to analyze for safety violations
    
    Returns:
        dict: Moderation results containing:
            - flagged (bool): Whether content violates any policies
            - categories (dict): Detailed breakdown by violation type:
                * hate: Hate speech content
                * hate/threatening: Threatening hate speech
                * self-harm: Self-harm related content
                * sexual: Sexual content
                * sexual/minors: Sexual content involving minors
                * violence: Violent content
                * violence/graphic: Graphic violent content
            - category_scores (dict): Confidence scores (0.0-1.0) for each category
            - error (str): Error message if API call fails
    
    Note:
        This function can be replaced with FloTorch's native guardrails system
        when available. See FloTorch documentation for GuardRailsInferencer usage.
    
    Example:
        >>> moderate_text("This is a safe marketing message")
        {
            'flagged': False,
            'categories': {'hate': False, 'violence': False, ...},
            'category_scores': {'hate': 0.001, 'violence': 0.002, ...}
        }
    
    Integration Notes:
        - For production: Consider implementing rate limiting
        - Add caching for repeated content analysis
        - Implement fallback moderation for API failures
        - Consider custom moderation rules for brand-specific policies
    """
    try:
        # Call OpenAI moderation endpoint with input text
        resp = openai.Moderation.create(input=text)
        
        # Extract moderation results from API response
        results = resp["results"][0]
        
        # Results structure includes:
        # - flagged: Boolean indicating policy violation
        # - categories: Dict of specific violation types
        # - category_scores: Confidence scores for each category
        return results
        
    except Exception as e:
        # Comprehensive error handling for API failures
        # Log error for monitoring and debugging
        print(f"Moderation API error: {str(e)}")
        
        # Return error information for upstream handling
        return {"error": str(e)}

# =============================================================================
# CONTENT REWRITING FUNCTIONS
# =============================================================================

def rewrite_safe(text: str, style: str = "remove_offensive") -> str:
    """
    Automatically rewrite content to remove policy violations while preserving intent.
    
    This function uses AI to intelligently rewrite flagged content, maintaining
    the original marketing message and intent while removing problematic elements.
    It's designed to provide a seamless user experience when content needs adjustment.
    
    Args:
        text (str): Original content that needs safety improvements
        style (str): Rewriting approach style, options include:
            - "remove_offensive": Remove problematic content (default)
            - "professional": Make content more professional
            - "inclusive": Ensure inclusive language
            - "brand_safe": Align with brand safety guidelines
    
    Returns:
        str: Rewritten content that maintains intent while improving safety
    
    Raises:
        Exception: If rewriting API call fails or returns invalid response
    
    Example:
        >>> rewrite_safe("This product will destroy the competition!")
        "This product will outperform the competition!"
    
    Rewriting Strategies:
        1. Preserve core marketing message and value proposition
        2. Maintain target audience appeal and tone
        3. Remove or replace problematic language
        4. Ensure compliance with content policies
        5. Optimize for brand safety and inclusivity
    
    Production Considerations:
        - Implement content versioning for audit trails
        - Add human review workflows for sensitive rewrites
        - Cache rewritten content to avoid redundant API calls
        - Implement A/B testing for rewrite effectiveness
        - Add custom rewriting rules for brand-specific requirements
    """
    # Construct rewriting prompt with clear instructions
    # Emphasize preservation of marketing intent while improving safety
    prompt = (
        f"Rewrite the following text to remove any offensive or unsafe content, "
        f"while keeping the same marketing message and intent:\n\n{text}"
    )
    
    try:
        # Call OpenAI Chat API for intelligent content rewriting
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Cost-effective model for rewriting tasks
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,        # Low temperature for consistent, safe outputs
            max_tokens=400,         # Sufficient tokens for marketing content
        )
        
        # Extract and clean rewritten content
        rewritten_content = resp["choices"][0]["message"]["content"].strip()
        
        return rewritten_content
        
    except Exception as e:
        # Error handling for rewriting failures
        print(f"Content rewriting error: {str(e)}")
        
        # Return original text with warning if rewriting fails
        # This ensures application continues functioning
        return f"[Rewrite failed] {text}"

# =============================================================================
# ADVANCED GUARDRAILS INTEGRATION
# =============================================================================

"""
FloTorch Guardrails Integration Guide:

For production deployments, consider integrating with FloTorch's native
guardrails system for enhanced performance and customization:

1. GuardRailsInferencer Setup:
   ```python
   from flotorch.guardrails import GuardRailsInferencer
   
   # Wrap your model with guardrails
   protected_model = GuardRailsInferencer(
       base_model=your_flotorch_model,
       input_guards=[content_filter, bias_detector],
       output_guards=[safety_checker, brand_compliance]
   )
   ```

2. Custom Guard Implementation:
   ```python
   class CustomContentGuard:
       def __init__(self, rules):
           self.rules = rules
       
       def check(self, content):
           # Implement custom safety logic
           return safety_result
   ```

3. Real-time Monitoring:
   - Implement guardrail performance metrics
   - Track false positive/negative rates
   - Monitor content quality improvements
   - Analyze user satisfaction with rewritten content

4. Compliance Integration:
   - GDPR compliance for content processing
   - Industry-specific regulations (healthcare, finance)
   - Regional content standards
   - Accessibility guidelines compliance
"""

# =============================================================================
# UTILITY FUNCTIONS FOR ENHANCED SAFETY
# =============================================================================

def batch_moderate(texts: list) -> list:
    """
    Efficiently moderate multiple text samples in batch processing.
    
    Args:
        texts (list): List of text strings to moderate
    
    Returns:
        list: List of moderation results for each input text
    """
    results = []
    for text in texts:
        result = moderate_text(text)
        results.append(result)
    return results

def get_safety_score(moderation_result: dict) -> float:
    """
    Calculate overall safety score from moderation results.
    
    Args:
        moderation_result (dict): Result from moderate_text function
    
    Returns:
        float: Safety score from 0.0 (unsafe) to 1.0 (completely safe)
    """
    if "error" in moderation_result:
        return 0.5  # Neutral score for errors
    
    if moderation_result.get("flagged", False):
        return 0.0  # Unsafe content
    
    # Calculate score based on category confidence levels
    scores = moderation_result.get("category_scores", {})
    max_score = max(scores.values()) if scores else 0.0
    
    return 1.0 - max_score  # Invert score (lower violation confidence = higher safety)

# =============================================================================
# CONFIGURATION AND CUSTOMIZATION
# =============================================================================

# Safety thresholds for different content types
SAFETY_THRESHOLDS = {
    "marketing": 0.8,      # High safety requirement for marketing content
    "social_media": 0.7,   # Moderate safety for social platforms
    "internal": 0.6,       # Lower threshold for internal communications
    "draft": 0.5           # Minimal threshold for draft content
}

def is_content_safe(text: str, content_type: str = "marketing") -> bool:
    """
    Determine if content meets safety requirements for specific use case.
    
    Args:
        text (str): Content to evaluate
        content_type (str): Type of content determining safety threshold
    
    Returns:
        bool: Whether content meets safety requirements
    """
    moderation_result = moderate_text(text)
    safety_score = get_safety_score(moderation_result)
    threshold = SAFETY_THRESHOLDS.get(content_type, 0.7)
    
    return safety_score >= threshold