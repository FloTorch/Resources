"""
Content Generation & Monitoring Application

This Streamlit application provides an advanced content generation platform using FloTorch LLM models
with comprehensive monitoring, analytics, and safety features. The application supports multiple
model selection, content quality analysis, performance metrics, and moderation capabilities.

Key Features:
- Multi-model content generation (flotorc        # Generate exactly the requested number of variants, distributed across selected models
        variant_count = 0
        while variant_count < num_variants:
            for model in selected_models:
                if variant_count >= num_variants:
                    break
                # Create unique prompt for each variant to ensure diversity
                variant_number = len(results) + 1
                variant_prompt = full_prompt + f"\n\nVariant {variant_number}: Make this unique and creative."
                variant_count += 1h, flotorch/awsnova)
- Real-time performance monitoring (latency, tokens, cost)
- Content quality analysis (readability, moderation)
- Interactive UI with customizable parameters
- Comprehensive analytics dashboard with visualizations

Author: Technical Team
Version: 1.0
Dependencies: streamlit, flotorch-sdk, pandas, matplotlib, requests
"""

# =============================================================================
# IMPORTS AND DEPENDENCIES
# =============================================================================

import streamlit as st          # Web application framework for creating interactive UI
import os                      # Operating system interface for environment variables
from flotorch.sdk.llm import FlotorchLLM  # FloTorch SDK for LLM model integration
import requests                # HTTP library for API requests and error handling
import sys                     # System-specific parameters and functions
import pandas as pd            # Data manipulation and analysis library
import matplotlib.pyplot as plt # Plotting library for creating charts and visualizations
import re                      # Regular expressions for text processing

# =============================================================================
# APPLICATION CONFIGURATION
# =============================================================================

# Configure Streamlit page settings for optimal user experience
st.set_page_config(
    page_title="Content Generation & Monitoring",  # Browser tab title
    layout="wide"                                   # Use full width of browser
)
st.title("🧠 Marketing Content Comparison Agent")

# Initialize session state for form persistence
if 'flotorch_setup_confirmed' not in st.session_state:
    st.session_state.flotorch_setup_confirmed = False

# =============================================================================
# SECURITY AND API CONFIGURATION
# =============================================================================

# FloTorch Service Configuration
FLOTORCH_BASE_URL = "https://gateway.flotorch.cloud"  # FloTorch gateway endpoint

# =============================================================================
# CORE BUSINESS LOGIC FUNCTIONS
# =============================================================================

def generate_content_variant(prompt: str, model_name: str, api_key: str) -> dict:
    """
    Generate content using FloTorch LLM with comprehensive metrics tracking.
    
    This function handles the complete lifecycle of content generation including:
    - API request timing and latency measurement
    - Token usage tracking for cost analysis
    - Error handling and user feedback
    - Response formatting for downstream processing
    
    Args:
        prompt (str): The input prompt for content generation
        model_name (str): FloTorch model identifier (default: flotorch/gflash)
    
    Returns:
        dict: Structured response containing:
            - text: Generated content string
            - tokens: Token count for cost calculation
            - latency_s: Response time in seconds
            - cost_estimate: Estimated API cost in USD
            - model_name: Model used for generation
        None: If generation fails due to API errors
    
    Raises:
        RequestException: For network-related API failures
        KeyError: For malformed API responses
        IndexError: For unexpected response structure
    """
    import time
    
    # Performance monitoring: Start timing for latency calculation
    start_time = time.time()
    
    # Format prompt according to FloTorch API requirements
    messages = [{"role": "user", "content": prompt}]
    
    # Initialize FloTorch LLM client with authentication and endpoint configuration
    model = FlotorchLLM(
        model_id=model_name, 
        api_key=api_key, 
        base_url=FLOTORCH_BASE_URL
    )

    try:
        # Execute API call to FloTorch service
        response = model.invoke(messages)
        
        # Extract response data with safe fallbacks
        text = extract_first_option(response.content)
        tokens_used = response.metadata.get("totalTokens", "N/A")
        latency = time.time() - start_time
        
        # Cost estimation based on token usage with model-specific pricing
        cost_estimate = calculate_model_cost(model_name, response.metadata) if isinstance(tokens_used, int) else 0.001
        
        # Return structured response for analytics processing
        return {
            "text": text,
            "tokens": tokens_used,
            "latency_s": round(latency, 2),
            "cost_estimate": round(cost_estimate, 4),
            "model_name": model_name
        }
        
    except (requests.exceptions.RequestException, KeyError, IndexError) as e:
        # Comprehensive error handling with user feedback
        st.error(f"⚠️ Error contacting model: {e}")
        
        # Debug information for troubleshooting
        if 'response' in locals() and hasattr(response, 'text'):
            st.code(response.text, language='json')
            
        return None

def build_enhanced_prompt(topic: str, product_name: str, tone: str, length: str, 
                         content_type: str, target_audience: str, cta: str) -> str:
    """
    Construct a comprehensive prompt from user inputs for optimal content generation.
    
    This function creates context-rich prompts that guide the LLM to generate
    high-quality, targeted content by incorporating all user-specified parameters.
    
    Args:
        topic (str): Main subject or theme for content
        product_name (str): Specific product being promoted
        tone (str): Desired communication style (professional, friendly, etc.)
        length (str): Target content length (short, medium, long)
        content_type (str): Format type (LinkedIn post, email, blog, etc.)
        target_audience (str): Intended audience demographic
        cta (str): Call-to-action text to include
    
    Returns:
        str: Formatted prompt string optimized for LLM content generation
    """
    # Base prompt establishing the AI's role and context
    prompt = f"You are a marketing content writer creating a {content_type.lower()}."
    
    # Conditionally add product information if provided
    if product_name:
        prompt += f"\\nProduct: {product_name}"
    
    # Core topic - always included as primary content focus
    prompt += f"\\nTopic: {topic}"
    
    # Target audience specification for content personalization
    if target_audience:
        prompt += f"\\nTarget audience: {target_audience}"
    
    # Style and format specifications
    prompt += f"\\nTone: {tone}"
    prompt += f"\\nLength: {length}"
    
    # Call-to-action integration for conversion optimization
    if cta:
        prompt += f"\\nInclude this call to action: {cta}"
    
    # Final instruction for quality and appropriateness - explicitly request single output
    prompt += "\\n\\nMake it engaging, clear, and appropriate for the specified tone and audience. Generate only ONE complete response, not multiple options or variations."
    
    return prompt

def simple_moderation_check(text: str) -> dict:
    """
    Perform basic content moderation to identify potentially problematic content.
    
    This is a simplified implementation for demonstration purposes. In production,
    integrate with professional moderation services like AWS Comprehend, OpenAI
    Moderation API, or similar enterprise-grade solutions.
    
    Args:
        text (str): Content text to analyze for policy violations
    
    Returns:
        dict: Moderation result containing:
            - flagged (bool): Whether content violates policies
            - reason (str): Explanation of violation (if any)
    """
    # Define prohibited content patterns
    # Note: This is a basic implementation - expand based on content policies
    flagged_words = ['spam', 'scam', 'fake', 'illegal']
    
    # Case-insensitive pattern matching
    flagged = any(word.lower() in text.lower() for word in flagged_words)
    
    return {
        "flagged": flagged, 
        "reason": "Contains potentially problematic content" if flagged else None
    }

def calculate_model_cost(model_name: str, metadata: dict) -> float:
    """
    Calculate accurate cost based on model-specific pricing and input/output tokens.
    
    Args:
        model_name (str): Model identifier (flotorch/gflash or flotorch/awsnova)
        metadata (dict): Response metadata containing token usage
    
    Returns:
        float: Estimated cost in USD
    """
    # Extract token counts from metadata
    input_tokens = metadata.get("inputTokens", 0)
    output_tokens = metadata.get("outputTokens", 0)
    total_tokens = metadata.get("totalTokens", input_tokens + output_tokens)
    
    # If input/output breakdown not available, estimate 70% input, 30% output
    if input_tokens == 0 and output_tokens == 0 and total_tokens > 0:
        input_tokens = int(total_tokens * 0.7)
        output_tokens = int(total_tokens * 0.3)
    
    # Model-specific pricing (per 1000 tokens)
    if "awsnova" in model_name.lower():
        # Nova micro model pricing
        input_cost = (input_tokens / 1000) * 0.000035
        output_cost = (output_tokens / 1000) * 0.00014
    elif "gflash" in model_name.lower():
        # Gemini flash model pricing  
        input_cost = (input_tokens / 1000000) * 0.1
        output_cost = (output_tokens / 1000000) * 0.4
    else:
        # Fallback pricing
        input_cost = (input_tokens / 1000) * 0.001
        output_cost = (output_tokens / 1000) * 0.002
    
    total_cost = input_cost + output_cost
    return round(total_cost, 6)

def extract_first_option(text: str) -> str:
    """
    Extract only the first option if model generates multiple choices.
    
    Args:
        text (str): Generated content that may contain multiple options
        
    Returns:
        str: First option only
    """
    # Common patterns for multiple options
    option_patterns = [
        r'Option \d+:',
        r'\d+\.',
        r'Version \d+:',
        r'Alternative \d+:',
        r'Choice \d+:'
    ]
    
    # Check if text contains multiple options
    for pattern in option_patterns:
        if len(re.findall(pattern, text, re.IGNORECASE)) > 1:
            # Split by the pattern and take first option
            parts = re.split(pattern, text, flags=re.IGNORECASE)
            if len(parts) > 1:
                # Return first meaningful part (skip empty first part)
                first_option = parts[1] if parts[0].strip() == '' else parts[0]
                return first_option.strip()
    
    return text.strip()

def calculate_readability(text: str) -> dict:
    """
    Calculate readability metrics to assess content accessibility and quality.
    
    Implements a simplified version of the Flesch Reading Ease score, which
    correlates with reading difficulty and audience comprehension levels.
    Higher scores indicate easier readability.
    
    Args:
        text (str): Content text to analyze
    
    Returns:
        dict: Readability metrics including:
            - flesch_reading_ease (float): Readability score (0-100)
            - avg_words_per_sentence (float): Average sentence length
            - word_count (int): Total word count
    """
    # Basic text analysis
    words = len(text.split())
    sentences = text.count('.') + text.count('!') + text.count('?') + 1
    avg_words_per_sentence = words / sentences if sentences > 0 else 0
    
    # Flesch Reading Ease calculation (simplified)
    # Formula: 206.835 - (1.015 × ASL) - (84.6 × ASW)
    # Where ASL = Average Sentence Length, ASW = Average Syllables per Word
    # Note: This implementation omits syllable counting for simplicity
    flesch_score = 206.835 - (1.015 * avg_words_per_sentence)
    
    return {
        "flesch_reading_ease": round(max(0, min(100, flesch_score)), 1),
        "avg_words_per_sentence": round(avg_words_per_sentence, 1),
        "word_count": words
    }

# =============================================================================
# USER INTERFACE COMPONENTS
# =============================================================================

# Sidebar Configuration Panel
# Provides centralized control for all generation parameters
with st.sidebar:
    st.info("🎉 Tip: Creating a FREE FloTorch account and API key is quick — you can get started in minutes. It won't be a hassle!")
    st.header("🔑 **Step 1 of 3:**")
    st.markdown("#### FloTorch Setup (Required)")
    # FloTorch Setup Guide - moved to top for visibility
    st.markdown("📖 **[FloTorch Setup Guide](https://github.com/FloTorch/Resources/blob/main/setup/flotorch_setup.md)** - Follow this first!")
    # st.markdown("**Complete this section before proceeding:**")

    st.header("⚙️ **Step 2 of 3:**")
    st.markdown("#### Enter your FloTorch details (Required)")

    # FloTorch Credentials - Required user inputs
    flotorch_api_key = st.text_input(
        "FloTorch API Key", 
        type="password",
        placeholder="Enter your FloTorch API key",
        help="Get this from your FloTorch dashboard"
    )
    
    user_model_1 = st.text_input(
        "Your Model 1 Name", 
        placeholder="flotorch/model-name-1",
        help="Exact name of your first FloTorch model"
    )
    
    user_model_2 = st.text_input(
        "Your Model 2 Name", 
        placeholder="flotorch/model-name-2",
        help="Exact name of your second FloTorch model"
    )
    
    # Automatic validation for required fields (no button needed)
    credentials_complete = flotorch_api_key and user_model_1 and user_model_2
    
    # st.caption("**ℹ️ After filling in the final FloTorch field above, press ENTER to continue.**")
    if credentials_complete:
        st.session_state.flotorch_setup_confirmed = True
        st.success("✅ FloTorch setup complete! Proceed to content generation.")
    elif flotorch_api_key or user_model_1 or user_model_2:
        st.info("📝 Please fill in all FloTorch fields above to continue.")
    else:
        st.warning("⚠️ After filling in the final FloTorch field above, press ENTER to continue.")
    

    st.header("⚙️ **Step 3 of 3:**")
    st.markdown("#### Content Configurations (Optional)")

    # Content Type Selection
    # Determines the format and style expectations for generated content
    content_type = st.selectbox(
        "Content type", 
        ["LinkedIn post", "Marketing Email", "Blog Intro"]
    )
    
    # Tone Configuration
    # Influences the writing style and personality of generated content
    tone = st.selectbox(
        "Tone", 
        ["professional", "friendly", "playful", "urgent"]
    )
    
    # Length Specification
    # Guides the LLM on desired content length
    length = st.selectbox(
        "Length", 
        ["short", "medium", "long"],
        index=1
    )

# Setup Instructions for New Users
if not st.session_state.flotorch_setup_confirmed:
    st.error("🛑 **SETUP REQUIRED**: Please complete FloTorch setup in the left sidebar first!")
    st.markdown("""
    ### 🚀 Getting Started:
    1. **Follow the [FloTorch Setup Guide](https://github.com/FloTorch/Resources/blob/main/setup/flotorch_setup.md)** (link in left sidebar)
    2. **Create your FREE FloTorch account** at [flotorch.ai](https://console.flotorch.cloud/auth/signup?provider=flotorch/)
    3. **Generate your API key** from the FloTorch dashboard
    4. **Create at least 2 custom models** in your FloTorch account
    5. **Enter your credentials** in the left sidebar
    6. **Then return here** to generate content!
    """)
    st.stop()

# Main Input Section
# Collects user content requirements in organized layout
st.markdown("### ✍️ User Inputs")
st.success("✅ FloTorch setup complete! You can now generate content.")

# Default texts to prepopulate user input fields after FloTorch setup
default_topic = (
    "Create engaging post to promote FloTorch platform at AWS Hackathon happening online in October 2025. "
    "Include the link for the hackathon https://aws.amazon.com/startups/events/aws-generative-ai-hackathon-challenge-2025?lang=en-US"
)
default_cta = "Visit us at  https://www.flotorch.ai/"
default_audience = "GenAI Builders, Developers and Engineers"
default_product = "FloTorch.ai"

# Only set defaults when FloTorch setup is confirmed and the user hasn't already entered values
if st.session_state.get('flotorch_setup_confirmed'):
    if 'topic' not in st.session_state or not str(st.session_state.get('topic', '')).strip():
        st.session_state['topic'] = default_topic
    if 'custom_cta' not in st.session_state or not str(st.session_state.get('custom_cta', '')).strip():
        st.session_state['custom_cta'] = default_cta
    if 'target_audience' not in st.session_state or not str(st.session_state.get('target_audience', '')).strip():
        st.session_state['target_audience'] = default_audience
    if 'product_name' not in st.session_state or not str(st.session_state.get('product_name', '')).strip():
        st.session_state['product_name'] = default_product

# Two-column layout for efficient space utilization
col1, col2 = st.columns(2)

with col1:
    # Primary content inputs
    topic = st.text_area(
        "Topic", 
        placeholder="Describe the product/campaign/topic", 
        height=100,
        key='topic'
    )
    product_name = st.text_input(
        "Product Name", 
        placeholder="Enter product name",
        key='product_name'
    )

with col2:
    # Secondary content inputs
    custom_cta = st.text_input(
        "Call to action:", 
        key='custom_cta'
    )
    target_audience = st.text_input(
        "Target Audience", 
        placeholder="e.g., tech professionals, students",
        key='target_audience'
    )

# =============================================================================
# CONTENT GENERATION WORKFLOW
# =============================================================================

# Main generation trigger with comprehensive validation and processing
if st.button("🚀 Generate Content"):
    
    # Validate FloTorch credentials first
    if not st.session_state.flotorch_setup_confirmed:
        st.error("❌ Please complete FloTorch setup in the left sidebar first!")
        st.stop()
    
    # Input validation - ensure minimum required data
    if not topic.strip():
        st.warning("Please enter a topic first.")
        st.stop()

    # Construct optimized prompt from user inputs
    full_prompt = build_enhanced_prompt(
        topic, product_name, tone, length, 
        content_type, target_audience, custom_cta
    )
    
    # Model Selection Processing
    # Build list of active models based on user selection
    selected_models = []
    if user_model_1:
        selected_models.append(user_model_1)
    if user_model_2:
        selected_models.append(user_model_2)
    
    # Validate models are available
    if not selected_models:
        st.warning("No FloTorch models are available. Please check your setup.")
        st.stop()
    
    # Content Generation Process
    # Execute generation with progress indication and error handling
    with st.spinner("Generating content via FloTorch..."):
        results = []
        
        # Generate one output per selected model
        for model in selected_models:
            # Generate content with error handling
            result = generate_content_variant(full_prompt, model, flotorch_api_key)
            if result:
                results.append(result)
    
    # =============================================================================
    # RESULTS DISPLAY AND ANALYSIS
    # =============================================================================
    
    if results:
        # Content Display Section
        # Present generated variants in full-width layout for optimal readability
        st.header("✅ Generated Content via Your FloTorch Models")
        
        for idx, result in enumerate(results):
            # Content header with model identification
            st.subheader(f"{result['model_name']} Output")
            
            # Display generated content
            st.write(result["text"])
            
            # Content Safety Check
            # Implement moderation with rewrite capability for policy compliance
            mod_result = simple_moderation_check(result["text"])
            if mod_result["flagged"]:
                st.error(f"⚠️ Moderation flag: {mod_result['reason']}")
                
                # Provide rewrite option for flagged content
                if st.button(f"Rewrite {result['model_name']}", key=f"rewrite_{idx}"):
                    rewrite_prompt = f"Rewrite this content to be more appropriate and professional:\\n\\n{result['text']}"
                    rewritten = generate_content_variant(rewrite_prompt, result['model_name'], flotorch_api_key)
                    if rewritten:
                        st.success("Rewritten version:")
                        st.write(rewritten["text"])
            
            st.divider()  # Visual separation between variants
        
        # =============================================================================
        # ANALYTICS AND PERFORMANCE MONITORING
        # =============================================================================
        
        st.header("📊 Performance Analytics")
        
        # Comprehensive Metrics Collection
        # Gather all performance and quality metrics for analysis
        metrics_data = []
        for idx, result in enumerate(results):
            # Calculate content quality metrics
            readability = calculate_readability(result["text"])
            mod_result = simple_moderation_check(result["text"])
            
            # Compile comprehensive metrics record
            metrics_data.append({
                "Model": result["model_name"],
                "Tokens": result["tokens"],
                "Latency (s)": result["latency_s"],
                "Cost ($)": result["cost_estimate"],
                "Readability Score": readability["flesch_reading_ease"],
                "Word Count": readability["word_count"],
                 "Avg Words/Sentence": readability["avg_words_per_sentence"],
                "Moderation Status": "⚠️" if mod_result["flagged"] else "✅"
            })
        
        # Display comprehensive analytics table
        df = pd.DataFrame(metrics_data)
        st.dataframe(df, use_container_width=True)
        
        # =============================================================================
        # SUMMARY METRICS AND AGGREGATIONS
        # =============================================================================
        
        st.subheader("📋 Summary")
        
        # Calculate aggregate metrics across all variants
        # Handle different token data types from API responses
        total_tokens = sum(
            int(r["tokens"]) for r in results 
            if r["tokens"] != "N/A" and str(r["tokens"]).isdigit()
        )
        total_cost = sum(r["cost_estimate"] for r in results)
        avg_latency = sum(r["latency_s"] for r in results) / len(results)
        
        # Display summary metrics in organized columns
        summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
        
        with summary_col1:
            st.metric("Total Outputs", len(results))
        with summary_col2:
            st.metric("Total Tokens", total_tokens)
        with summary_col3:
            st.metric("Total Cost ($)", f"{total_cost:.4f}")
        with summary_col4:
            st.metric("Avg Latency (s)", f"{avg_latency:.2f}")
        
        # =============================================================================
        # PERFORMANCE VISUALIZATION
        # =============================================================================
        
        # Generate comparison charts for multi-variant analysis
        if len(results) > 1:
            st.subheader("📈 Performance Comparison")
            chart_col1, chart_col2 = st.columns(2)
            
            # Latency Comparison Chart
            with chart_col1:
                fig, ax = plt.subplots(figsize=(6, 4))
                ax.bar(
                    [r["model_name"].split("/")[-1] for r in results], 
                    [r["latency_s"] for r in results]
                )
                ax.set_title("Response Latency Comparison")
                ax.set_ylabel("Seconds")
                plt.tight_layout()
                st.pyplot(fig)
            
            # Cost Comparison Chart
            with chart_col2:
                fig, ax = plt.subplots(figsize=(6, 4))
                ax.bar(
                    [r["model_name"].split("/")[-1] for r in results], 
                    [r["cost_estimate"] for r in results]
                )
                ax.set_title("Estimated Cost Comparison")
                ax.set_ylabel("USD")
                plt.tight_layout()
                st.pyplot(fig)
        
        # Success confirmation with result summary
        st.success(f"Generated {len(results)} outputs successfully!")
        
    else:
        # Error handling for failed generation attempts
        st.error("Failed to generate content. Please check your configuration.")

# =============================================================================
# FEATURE OVERVIEW AND DOCUMENTATION
# =============================================================================

# Enhanced monitoring section - showcases platform capabilities
st.divider()
st.markdown("### 🔍 Advanced Monitoring Features")

# Feature categories with detailed descriptions
col1, col2, col3 = st.columns(3)

with col1:
    st.info("""**Content Quality**
- Readability scores
- Tone analysis  
- Bias detection""")

with col2:
    st.info("""**Performance**
- Response latency
- Token usage
- Cost tracking""")

with col3:
    st.info("""**Safety & Compliance**
- Content moderation
- Guardrails
- Rewrite suggestions""")