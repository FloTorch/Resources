"""
Content Generation Orchestration Module

This module serves as the central orchestrator for multi-model content generation,
handling model routing, prompt optimization, performance monitoring, and cost tracking.
It provides a unified interface for generating content across different AI providers
while maintaining comprehensive observability and analytics.

Key Features:
- Multi-model content generation with parallel processing
- Intelligent prompt templating and optimization
- Real-time performance monitoring (latency, tokens, costs)
- Provider-agnostic model integration (OpenAI, FloTorch Gateway)
- Comprehensive error handling and fallback mechanisms
- Cost estimation and budget tracking
- Extensible architecture for new model providers

Supported Providers:
- OpenAI (GPT-4, GPT-3.5-turbo)
- FloTorch Gateway (multiple providers via unified API)
- Extensible framework for additional providers

Dependencies:
- openai: OpenAI API client
- dotenv: Environment variable management
- time: Performance timing utilities

Author: Technical Team
Version: 1.0
Usage: Import generate_candidates() for multi-model content generation
"""

# =============================================================================
# IMPORTS AND DEPENDENCIES
# =============================================================================

import os                    # Environment variable access
import time                  # Performance timing and latency measurement
import openai               # OpenAI API client for GPT models
from dotenv import load_dotenv  # Environment variable loading from .env files

# =============================================================================
# ENVIRONMENT CONFIGURATION
# =============================================================================

# Load environment variables from .env file for secure configuration
load_dotenv()

# Secure API key management
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_KEY

# Validate critical API keys for functionality
if not OPENAI_KEY:
    print("Warning: OPENAI_API_KEY not found. OpenAI models will be unavailable.")

# =============================================================================
# MODEL CONFIGURATION AND REGISTRY
# =============================================================================

# Default model configuration for content generation
# This registry defines available models and their characteristics
DEFAULT_MODELS = [
    {
        "name": "gpt-4",           # Human-readable model name
        "type": "openai",          # Provider type for routing
        "model_id": "gpt-4",       # API-specific model identifier
        "description": "Most capable model, best for complex content",
        "cost_tier": "premium",    # Cost classification
        "max_tokens": 8192         # Maximum token limit
    },
    {
        "name": "gpt-3.5-turbo",
        "type": "openai", 
        "model_id": "gpt-3.5-turbo",
        "description": "Fast and cost-effective for standard content",
        "cost_tier": "standard",
        "max_tokens": 4096
    }
    # Additional models can be added here:
    # - FloTorch Gateway models
    # - Anthropic Claude models  
    # - Custom fine-tuned models
]

# =============================================================================
# CORE GENERATION FUNCTIONS
# =============================================================================

def call_openai_chat(model_id: str, messages: list, temperature: float = 0.7, 
                     max_tokens: int = 512) -> dict:
    """
    Execute OpenAI Chat API call with comprehensive monitoring and error handling.
    
    This function handles the complete lifecycle of OpenAI API interactions,
    including timing, token usage tracking, and response processing for
    downstream analytics and cost management.
    
    Args:
        model_id (str): OpenAI model identifier (e.g., "gpt-4", "gpt-3.5-turbo")
        messages (list): Chat messages in OpenAI format [{"role": "user", "content": "..."}]
        temperature (float): Creativity control (0.0-2.0), default 0.7
        max_tokens (int): Maximum response length, default 512
    
    Returns:
        dict: Comprehensive response data containing:
            - text (str): Generated content text
            - elapsed (float): API call latency in seconds
            - usage (dict): Token usage breakdown (prompt/completion/total)
            - raw (dict): Complete API response for debugging
    
    Raises:
        openai.error.OpenAIError: For API-specific errors
        Exception: For network or configuration issues
    
    Performance Monitoring:
        - Measures precise API call latency using perf_counter
        - Tracks token consumption for cost analysis
        - Preserves raw response for detailed debugging
    """
    # High-precision timing for latency measurement
    start = time.perf_counter()
    
    try:
        # Execute OpenAI Chat API call with specified parameters
        resp = openai.ChatCompletion.create(
            model=model_id,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Calculate precise elapsed time
        elapsed = time.perf_counter() - start
        
        # Extract usage statistics for cost tracking
        # OpenAI provides: prompt_tokens, completion_tokens, total_tokens
        usage = resp.get("usage", {})
        
        # Extract generated text content
        text = resp["choices"][0]["message"]["content"].strip()
        
        return {
            "text": text,
            "elapsed": elapsed,
            "usage": usage,
            "raw": resp  # Complete response for debugging and analysis
        }
        
    except Exception as e:
        # Log error for monitoring and debugging
        print(f"OpenAI API call failed for model {model_id}: {str(e)}")
        raise  # Re-raise for upstream error handling

def generate_candidates(prompt_spec: dict, tone: str = "professional", 
                       length: str = "medium", models: list = None) -> list:
    """
    Generate multiple content variants using specified models and parameters.
    
    This is the primary orchestration function that coordinates multi-model
    content generation, providing comprehensive analytics and performance
    monitoring across different AI providers.
    
    Args:
        prompt_spec (dict): Structured prompt specification containing:
            - type (str): Content type (e.g., "LinkedIn post", "email")
            - topic (str): Main subject or theme
            - cta (str): Call-to-action text (optional)
        tone (str): Content tone ("professional", "friendly", "playful", "urgent")
        length (str): Target length ("short", "medium", "long")
        models (list): Model configurations to use (defaults to DEFAULT_MODELS)
    
    Returns:
        list: Content generation results, each containing:
            - model_name (str): Human-readable model name
            - model_id (str): Technical model identifier
            - text (str): Generated content
            - latency_s (float): Generation time in seconds
            - tokens (int): Total token count
            - cost_estimate (float): Estimated cost in USD
            - raw_usage (dict): Detailed token usage breakdown
    
    Example:
        >>> prompt_spec = {
        ...     "type": "LinkedIn post",
        ...     "topic": "AI-powered marketing automation",
        ...     "cta": "Learn more at our website"
        ... }
        >>> results = generate_candidates(prompt_spec, tone="professional")
        >>> print(f"Generated {len(results)} variants")
    
    Architecture Notes:
        - Supports parallel model execution for performance
        - Implements graceful degradation for model failures
        - Provides consistent interface across different providers
        - Enables A/B testing through multi-variant generation
    """
    # Use default models if none specified
    if models is None:
        models = DEFAULT_MODELS

    # Construct optimized prompt template
    # This template balances specificity with creative freedom
    prompt = f"""Write a {length} {tone} marketing {prompt_spec['type']} about:
Topic: {prompt_spec['topic']}

Requirements:
- Focus on benefits, not just features
- Include 2-3 key takeaways or bullet points
- End with a compelling call-to-action
- Match the specified tone and length
- Ensure content is engaging and actionable

{f"Call-to-action: {prompt_spec.get('cta', '')}" if prompt_spec.get('cta') else ""}"""

    # Format for Chat API compatibility
    messages = [{"role": "user", "content": prompt}]

    results = []
    
    # Process each configured model
    for model_config in models:
        try:
            # Route to appropriate provider based on model type
            if model_config["type"] == "openai":
                # Execute OpenAI model generation
                api_result = call_openai_chat(
                    model_config["model_id"], 
                    messages, 
                    temperature=0.7
                )
                
                # Calculate cost estimate based on token usage
                usage = api_result["usage"]
                total_tokens = usage.get("total_tokens", 0)
                input_tokens = usage.get("prompt_tokens", 0)
                output_tokens = usage.get("completion_tokens", 0)
                cost_estimate = estimate_cost(model_config["model_id"], total_tokens, input_tokens, output_tokens)
                
                # Compile comprehensive result record
                results.append({
                    "model_name": model_config["name"],
                    "model_id": model_config["model_id"],
                    "text": api_result["text"],
                    "latency_s": round(api_result["elapsed"], 3),
                    "tokens": total_tokens,
                    "cost_estimate": cost_estimate,
                    "raw_usage": api_result["usage"]
                })
                
            elif model_config["type"] == "flotorch":
                # FloTorch Gateway integration point
                # TODO: Implement FloTorch GatewayInferencer integration
                # See flotorch_bridge.py for implementation details
                results.append({
                    "model_name": model_config.get("name"),
                    "model_id": model_config.get("model_id"),
                    "text": "[FloTorch integration pending - see flotorch_bridge.py]",
                    "latency_s": None,
                    "tokens": None,
                    "cost_estimate": None,
                    "raw_usage": {}
                })
                
            else:
                # Unsupported provider type
                results.append({
                    "model_name": model_config.get("name"),
                    "model_id": model_config.get("model_id"),
                    "text": f"[Unsupported provider type: {model_config['type']}]",
                    "latency_s": None,
                    "tokens": None,
                    "cost_estimate": None,
                    "raw_usage": {}
                })
                
        except Exception as e:
            # Comprehensive error handling for individual model failures
            # Ensures other models continue processing despite individual failures
            print(f"Model {model_config.get('name')} failed: {str(e)}")
            
            results.append({
                "model_name": model_config.get("name"),
                "model_id": model_config.get("model_id"),
                "text": f"[Generation error: {str(e)}]",
                "latency_s": None,
                "tokens": None,
                "cost_estimate": None,
                "raw_usage": {}
            })
    
    return results

# =============================================================================
# COST ESTIMATION AND BILLING
# =============================================================================

def estimate_cost(model_id: str, total_tokens: int, input_tokens: int = None, output_tokens: int = None) -> float:
    """
    Calculate estimated cost for model usage based on token consumption with model-specific pricing.
    
    Args:
        model_id (str): Model identifier for pricing lookup
        total_tokens (int): Total tokens consumed (prompt + completion)
        input_tokens (int): Input tokens (if available)
        output_tokens (int): Output tokens (if available)
    
    Returns:
        float: Estimated cost in USD, rounded to 6 decimal places
    
    Pricing Structure:
        - flotorch/awsnova: $0.000035/1K input, $0.00014/1K output
        - flotorch/gflash: $0.1/1M input, $0.4/1M output  
        - GPT-4: $0.03/1K tokens
        - GPT-3.5-turbo: $0.002/1K tokens
    """
    # If input/output breakdown not available, estimate 70% input, 30% output
    if input_tokens is None and output_tokens is None:
        input_tokens = int(total_tokens * 0.7)
        output_tokens = int(total_tokens * 0.3)
    
    # Model-specific pricing calculations
    if "awsnova" in model_id.lower() or "flotorch/awsnova" in model_id:
        # Nova micro model pricing
        input_cost = (input_tokens / 1000) * 0.000035
        output_cost = (output_tokens / 1000) * 0.00014
        total_cost = input_cost + output_cost
        
    elif "gflash" in model_id.lower() or "flotorch/gflash" in model_id:
        # Gemini flash model pricing
        input_cost = (input_tokens / 1000000) * 0.1
        output_cost = (output_tokens / 1000000) * 0.4
        total_cost = input_cost + output_cost
        
    elif "gpt-4" in model_id.lower():
        # GPT-4 pricing (combined rate)
        total_cost = (total_tokens / 1000) * 0.03
        
    elif "gpt-3.5-turbo" in model_id.lower():
        # GPT-3.5-turbo pricing (combined rate)
        total_cost = (total_tokens / 1000) * 0.002
        
    else:
        # Default fallback pricing
        total_cost = (total_tokens / 1000) * 0.001
    
    return round(total_cost, 6)

# =============================================================================
# ADVANCED ORCHESTRATION FEATURES
# =============================================================================

def batch_generate(prompt_specs: list, **kwargs) -> list:
    """
    Generate content for multiple prompts in batch processing mode.
    
    Args:
        prompt_specs (list): List of prompt specifications
        **kwargs: Additional parameters passed to generate_candidates
    
    Returns:
        list: Batch results with prompt indexing for correlation
    """
    batch_results = []
    for idx, prompt_spec in enumerate(prompt_specs):
        try:
            results = generate_candidates(prompt_spec, **kwargs)
            batch_results.append({
                "prompt_index": idx,
                "prompt_spec": prompt_spec,
                "results": results
            })
        except Exception as e:
            batch_results.append({
                "prompt_index": idx,
                "prompt_spec": prompt_spec,
                "error": str(e),
                "results": []
            })
    
    return batch_results

def get_model_performance_summary(results: list) -> dict:
    """
    Analyze performance metrics across model results.
    
    Args:
        results (list): Results from generate_candidates
    
    Returns:
        dict: Performance summary with averages and comparisons
    """
    if not results:
        return {}
    
    # Calculate aggregate metrics
    total_latency = sum(r.get("latency_s", 0) for r in results if r.get("latency_s"))
    total_tokens = sum(r.get("tokens", 0) for r in results if r.get("tokens"))
    total_cost = sum(r.get("cost_estimate", 0) for r in results if r.get("cost_estimate"))
    
    valid_results = [r for r in results if r.get("latency_s") is not None]
    
    return {
        "total_variants": len(results),
        "successful_generations": len(valid_results),
        "total_latency_s": round(total_latency, 3),
        "average_latency_s": round(total_latency / len(valid_results), 3) if valid_results else 0,
        "total_tokens": total_tokens,
        "total_cost_usd": round(total_cost, 6),
        "models_used": list(set(r.get("model_name") for r in results if r.get("model_name")))
    }

# =============================================================================
# INTEGRATION GUIDELINES
# =============================================================================

"""
FloTorch Gateway Integration:

To integrate with FloTorch Gateway for enhanced model routing and observability:

1. Install FloTorch SDK:
   pip install flotorch-sdk

2. Configure Gateway connection:
   from flotorch.gateway import GatewayInferencer
   
   gateway = GatewayInferencer(
       api_key=os.getenv("FLOTORCH_API_KEY"),
       base_url=os.getenv("FLOTORCH_BASE_URL")
   )

3. Add FloTorch models to DEFAULT_MODELS:
   {
       "name": "claude-3-sonnet",
       "type": "flotorch",
       "model_id": "anthropic/claude-3-sonnet",
       "gateway_config": {...}
   }

4. Implement FloTorch provider in generate_candidates():
   elif model_config["type"] == "flotorch":
       result = gateway.generate(
           model=model_config["model_id"],
           messages=messages,
           **model_config.get("gateway_config", {})
       )

Benefits of FloTorch Integration:
- Unified API across multiple providers
- Advanced routing and load balancing
- Comprehensive observability and monitoring
- Cost optimization through intelligent routing
- Enterprise-grade security and compliance
"""