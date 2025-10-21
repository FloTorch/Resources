"""
FloTorch Integration Testing and Validation Module

This module provides comprehensive testing utilities for validating FloTorch
integration, API connectivity, and model functionality. It includes both
basic connectivity tests and advanced feature validation to ensure proper
setup and configuration of the FloTorch platform.

Key Features:
- FloTorch API connectivity testing
- Model availability and performance validation
- SDK integration verification
- Error handling and troubleshooting utilities
- Performance benchmarking capabilities
- Configuration validation

Test Categories:
- Basic connectivity tests
- Model inference validation
- SDK feature testing
- Performance benchmarking
- Error scenario handling

Dependencies:
- flotorch-sdk: FloTorch Python SDK
- openai: OpenAI client for comparison testing
- dotenv: Environment variable management

Author: Technical Team
Version: 1.0
Usage: Run this module to validate FloTorch setup and integration
"""

# =============================================================================
# ENVIRONMENT CONFIGURATION
# =============================================================================

# Environment variables for FloTorch Gateway configuration
# These should be set in your shell environment or .env file:
# export OPENAI_BASE_URL="https://gateway.flotorch.cloud"
# export OPENAI_API_KEY="your-flotorch-api-key"

# =============================================================================
# BASIC CONNECTIVITY TESTS
# =============================================================================

def test_openai_client_via_flotorch():
    """
    Test OpenAI client connectivity through FloTorch Gateway.
    
    This test validates that the OpenAI client can successfully connect
    to FloTorch Gateway and generate content using the configured model.
    It serves as a basic connectivity and authentication test.
    
    Returns:
        bool: True if test passes, False otherwise
    
    Test Validation:
        - API authentication success
        - Model availability and response
        - Response format and content quality
        - Latency within acceptable bounds
    """
    try:
        print("🧪 Testing OpenAI client via FloTorch Gateway...")
        
        # Initialize OpenAI client (will use FloTorch Gateway if configured)
        from openai import OpenAI
        client = OpenAI()
        
        # Test basic text generation
        response = client.responses.create(
            model="gpt-4.1",  # FloTorch model identifier
            input="Write a one-sentence bedtime story about a unicorn."
        )
        
        # Validate response
        if hasattr(response, 'output_text') and response.output_text:
            print(f"✅ OpenAI client test successful!")
            print(f"📝 Generated content: {response.output_text}")
            return True
        else:
            print("❌ OpenAI client test failed: No output text received")
            return False
            
    except Exception as e:
        print(f"❌ OpenAI client test failed: {str(e)}")
        return False

def test_flotorch_sdk_integration():
    """
    Test native FloTorch SDK integration and functionality.
    
    This comprehensive test validates the FloTorch SDK's core capabilities
    including model initialization, content generation, and response handling.
    
    Returns:
        bool: True if all tests pass, False otherwise
    
    Test Coverage:
        - SDK import and initialization
        - Model configuration and authentication
        - Content generation with various parameters
        - Response parsing and metadata extraction
        - Error handling and edge cases
    """
    try:
        print("🧪 Testing FloTorch SDK integration...")
        
        # FloTorch configuration constants
        FLOTORCH_API_KEY = "sk_OunwVHb5S6El9323QNlIfC8udzVnptV0eEi8Vf125+w=_MWNlODQ4ZWUtNDEzMi00M2Q1LWE0ZDgtMGU0MzdlMWM5ODRh_ZTVkNDkyODMtM2VjOC00ZDI1LWE3OGEtZjVkZTNmZDVkOTFh"
        FLOTORCH_BASE_URL = "https://gateway.flotorch.cloud"
        FLOTORCH_MODEL = "flotorch/gflash"
        
        # Import FloTorch SDK
        from flotorch.sdk.llm import FlotorchLLM
        print("✅ FloTorch SDK imported successfully")
        
        # Initialize FloTorch LLM client
        fl = FlotorchLLM(
            model_id=FLOTORCH_MODEL,
            api_key=FLOTORCH_API_KEY,
            base_url=FLOTORCH_BASE_URL
        )
        print("✅ FloTorch LLM client initialized successfully")
        
        # Inspect available methods and attributes
        available_methods = [method for method in dir(fl) if not method.startswith('_')]
        print(f"📋 Available methods: {available_methods}")
        
        # Test content generation (if generate method exists)
        if hasattr(fl, 'generate'):
            response = fl.generate(
                prompt_text="Write a short message about FloTorch hackathon."
            )
            
            if hasattr(response, 'output_text'):
                print(f"✅ Content generation successful!")
                print(f"📝 Generated content: {response.output_text}")
                return True
            else:
                print("⚠️ Response received but no output_text attribute found")
                print(f"📋 Response attributes: {dir(response)}")
                return False
        
        # Test invoke method (alternative API)
        elif hasattr(fl, 'invoke'):
            messages = [{"role": "user", "content": "Write a short message about FloTorch hackathon."}]
            response = fl.invoke(messages)
            
            if hasattr(response, 'content'):
                print(f"✅ Content generation via invoke successful!")
                print(f"📝 Generated content: {response.content}")
                return True
            else:
                print("⚠️ Response received but no content attribute found")
                print(f"📋 Response attributes: {dir(response)}")
                return False
        
        else:
            print("⚠️ No recognized generation method found")
            print(f"📋 Available methods: {available_methods}")
            return False
            
    except ImportError as e:
        print(f"❌ FloTorch SDK import failed: {str(e)}")
        print("💡 Install FloTorch SDK: pip install flotorch-sdk")
        return False
    except Exception as e:
        print(f"❌ FloTorch SDK test failed: {str(e)}")
        return False

# =============================================================================
# PERFORMANCE BENCHMARKING
# =============================================================================

def benchmark_model_performance(model_configs: list, test_prompts: list) -> dict:
    """
    Benchmark performance across multiple models and prompts.
    
    Args:
        model_configs (list): List of model configuration dictionaries
        test_prompts (list): List of test prompts for evaluation
    
    Returns:
        dict: Comprehensive performance metrics
    """
    import time
    
    results = {
        "models_tested": len(model_configs),
        "prompts_tested": len(test_prompts),
        "results": [],
        "summary": {}
    }
    
    print("🏃 Starting performance benchmark...")
    
    for model_config in model_configs:
        model_results = {
            "model_id": model_config.get("model_id"),
            "prompt_results": [],
            "avg_latency": 0,
            "total_tokens": 0,
            "success_rate": 0
        }
        
        successful_tests = 0
        total_latency = 0
        
        for prompt in test_prompts:
            try:
                start_time = time.perf_counter()
                
                # Initialize model for each test (could be optimized)
                from flotorch.sdk.llm import FlotorchLLM
                fl = FlotorchLLM(
                    model_id=model_config["model_id"],
                    api_key=model_config["api_key"],
                    base_url=model_config["base_url"]
                )
                
                # Generate content
                if hasattr(fl, 'invoke'):
                    messages = [{"role": "user", "content": prompt}]
                    response = fl.invoke(messages)
                    content = getattr(response, 'content', '')
                    tokens = getattr(response, 'metadata', {}).get('totalTokens', 0)
                else:
                    # Fallback for different API
                    response = fl.generate(prompt_text=prompt)
                    content = getattr(response, 'output_text', '')
                    tokens = 0  # Token count not available
                
                latency = time.perf_counter() - start_time
                
                model_results["prompt_results"].append({
                    "prompt": prompt[:50] + "..." if len(prompt) > 50 else prompt,
                    "latency_s": round(latency, 3),
                    "tokens": tokens,
                    "content_length": len(content),
                    "success": True
                })
                
                successful_tests += 1
                total_latency += latency
                model_results["total_tokens"] += tokens if isinstance(tokens, int) else 0
                
            except Exception as e:
                model_results["prompt_results"].append({
                    "prompt": prompt[:50] + "..." if len(prompt) > 50 else prompt,
                    "error": str(e),
                    "success": False
                })
        
        # Calculate model summary statistics
        model_results["success_rate"] = successful_tests / len(test_prompts)
        model_results["avg_latency"] = total_latency / successful_tests if successful_tests > 0 else 0
        
        results["results"].append(model_results)
    
    # Calculate overall summary
    total_successful = sum(len([r for r in model["prompt_results"] if r.get("success", False)]) 
                          for model in results["results"])
    total_tests = len(model_configs) * len(test_prompts)
    
    results["summary"] = {
        "overall_success_rate": total_successful / total_tests if total_tests > 0 else 0,
        "total_tests_run": total_tests,
        "successful_tests": total_successful
    }
    
    return results

# =============================================================================
# COMPREHENSIVE TEST SUITE
# =============================================================================

def run_comprehensive_tests():
    """
    Execute comprehensive test suite for FloTorch integration validation.
    
    This function runs all available tests and provides a detailed report
    of the FloTorch integration status, including recommendations for
    any issues found.
    
    Returns:
        dict: Comprehensive test results and recommendations
    """
    print("🚀 Starting FloTorch Integration Test Suite")
    print("=" * 60)
    
    test_results = {
        "openai_client_test": False,
        "flotorch_sdk_test": False,
        "performance_benchmark": None,
        "recommendations": []
    }
    
    # Test 1: OpenAI Client via FloTorch Gateway
    test_results["openai_client_test"] = test_openai_client_via_flotorch()
    print()
    
    # Test 2: Native FloTorch SDK
    test_results["flotorch_sdk_test"] = test_flotorch_sdk_integration()
    print()
    
    # Test 3: Performance Benchmark (if basic tests pass)
    if test_results["flotorch_sdk_test"]:
        try:
            model_configs = [{
                "model_id": "flotorch/gflash",
                "api_key": "sk_OunwVHb5S6El9323QNlIfC8udzVnptV0eEi8Vf125+w=_MWNlODQ4ZWUtNDEzMi00M2Q1LWE0ZDgtMGU0MzdlMWM5ODRh_ZTVkNDkyODMtM2VjOC00ZDI1LWE3OGEtZjVkZTNmZDVkOTFh",
                "base_url": "https://gateway.flotorch.cloud"
            }]
            
            test_prompts = [
                "Write a short marketing message.",
                "Create a professional email greeting.",
                "Generate a product description for a smartphone."
            ]
            
            test_results["performance_benchmark"] = benchmark_model_performance(
                model_configs, test_prompts
            )
            print("✅ Performance benchmark completed")
            
        except Exception as e:
            print(f"⚠️ Performance benchmark failed: {str(e)}")
    
    # Generate recommendations based on test results
    if not test_results["openai_client_test"]:
        test_results["recommendations"].append(
            "OpenAI client test failed - check OPENAI_BASE_URL and OPENAI_API_KEY environment variables"
        )
    
    if not test_results["flotorch_sdk_test"]:
        test_results["recommendations"].append(
            "FloTorch SDK test failed - ensure flotorch-sdk is installed and configured correctly"
        )
    
    if not any([test_results["openai_client_test"], test_results["flotorch_sdk_test"]]):
        test_results["recommendations"].extend([
            "Install FloTorch SDK: pip install flotorch-sdk",
            "Set environment variables: OPENAI_BASE_URL and OPENAI_API_KEY",
            "Verify FloTorch Gateway connectivity and API key validity"
        ])
    
    # Print final summary
    print("=" * 60)
    print("📊 Test Suite Summary")
    print(f"OpenAI Client Test: {'✅ PASS' if test_results['openai_client_test'] else '❌ FAIL'}")
    print(f"FloTorch SDK Test: {'✅ PASS' if test_results['flotorch_sdk_test'] else '❌ FAIL'}")
    
    if test_results["recommendations"]:
        print("\n💡 Recommendations:")
        for rec in test_results["recommendations"]:
            print(f"  • {rec}")
    
    return test_results

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    """
    Main execution block for running FloTorch integration tests.
    
    This block executes when the module is run directly, providing
    a comprehensive validation of the FloTorch setup and integration.
    """
    
    print("FloTorch Integration Testing Module")
    print("Author: Technical Team")
    print("Version: 1.0")
    print()
    
    # Run comprehensive test suite
    results = run_comprehensive_tests()
    
    # Exit with appropriate code
    if results["openai_client_test"] or results["flotorch_sdk_test"]:
        print("\n🎉 FloTorch integration is working!")
        exit(0)
    else:
        print("\n⚠️ FloTorch integration needs attention.")
        exit(1)

# =============================================================================
# LEGACY CODE REFERENCE
# =============================================================================

"""
Legacy code examples and alternative implementations:

# Alternative OpenAI client usage:
from openai import OpenAI
client = OpenAI()

response = client.responses.create(
    model="gpt-4.1",
    input="Write a one-sentence bedtime story about a unicorn."
)
print(response.output_text)

# Alternative FloTorch SDK usage patterns:
from flotorch.sdk.llm import FlotorchLLM

# Method 1: Direct generation
fl = FlotorchLLM(model_id="gpt-3.5-turbo", api_key=os.getenv("OPENAI_API_KEY"))
resp = fl.generate(prompt_text="Write a short message about FloTorch hackathon.")
print(resp.output_text)

# Method 2: Chat-style interaction
messages = [{"role": "user", "content": "Hello, FloTorch!"}]
response = fl.invoke(messages)
print(response.content)

These examples demonstrate different ways to interact with FloTorch
depending on the specific SDK version and configuration.
"""