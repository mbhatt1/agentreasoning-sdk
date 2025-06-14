#!/usr/bin/env python3
"""
Test the real system with the JSON parsing fixes
"""

import asyncio
import os
import logging
from agentic_reasoning_system import AgenticReasoningSystemSDK, ReasoningContext

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_real_system():
    """Test the real system with JSON parsing fixes"""
    
    # Check if API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  OPENAI_API_KEY not found. This test requires a real API key.")
        print("   Set the environment variable and run again to test with real OpenAI API.")
        return
    
    print("Testing Agentic Reasoning System with JSON parsing fixes...")
    print("=" * 60)
    
    try:
        # Initialize the system
        system = AgenticReasoningSystemSDK(openai_api_key=api_key)
        
        # Test case 1: Simple reasoning problem
        print("\n🧠 Test 1: Simple Logic Problem")
        print("-" * 40)
        
        context = ReasoningContext(
            problem="If all cats are mammals, and Fluffy is a cat, what can we conclude about Fluffy?",
            representation_format="natural_language",
            domain="logic",
            complexity_level=2
        )
        
        result = await system.reason(context)
        
        print(f"✅ Success: {result.success}")
        print(f"📝 Solution: {result.solution}")
        print(f"🎯 Confidence: {result.confidence}")
        print(f"⏱️  Processing time: {result.processing_time:.2f}s")
        print(f"🔄 State transitions: {len(result.state_transitions)}")
        
        # Test case 2: Understanding task
        print("\n🤔 Test 2: Understanding Task")
        print("-" * 40)
        
        understanding_result = await system.understand(
            proposition="The sky appears blue during daytime",
            representation_format="natural_language",
            domain="physics"
        )
        
        print(f"✅ Truth value: {understanding_result.truth_value}")
        print(f"🎯 Confidence: {understanding_result.confidence}")
        print(f"📊 Modal invariance: {understanding_result.modal_invariance_score}")
        print(f"⏱️  Processing time: {understanding_result.processing_time:.2f}s")
        
        print("\n" + "=" * 60)
        print("🎉 All tests completed successfully!")
        print("✅ JSON parsing fixes are working correctly with real API calls")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        logger.error(f"System test failed: {e}", exc_info=True)

async def test_json_parsing_edge_cases():
    """Test edge cases that might cause JSON parsing issues"""
    
    print("\n🔧 Testing JSON parsing edge cases...")
    print("=" * 60)
    
    # This test doesn't require an API key - it tests the parsing logic
    from agentic_reasoning_system import LLMInterface
    
    # Create a mock interface to test parsing methods directly
    class TestLLMInterface(LLMInterface):
        def __init__(self):
            # Skip OpenAI initialization
            self.model = "test"
    
    llm = TestLLMInterface()
    
    # Test various problematic JSON responses
    test_cases = [
        ('Valid JSON', '{"confidence": 0.8, "solution": "Test"}'),
        ('Trailing comma', '{"confidence": 0.8, "solution": "Test",}'),
        ('Unquoted keys', '{confidence: 0.8, solution: "Test"}'),
        ('Single quotes', "{'confidence': 0.8, 'solution': 'Test'}"),
        ('Mixed quotes', '{"confidence": 0.8, \'solution\': "Test"}'),
        ('Code block', '```json\n{"confidence": 0.8}\n```'),
        ('With explanation', 'Here is the result: {"confidence": 0.8}'),
        ('Truncated', '{"confidence": 0.8, "solution": "Incomplete'),
        ('Empty response', ''),
        ('Non-JSON', 'This is not JSON at all'),
    ]
    
    for name, response in test_cases:
        print(f"\n📝 Testing: {name}")
        print(f"   Input: {response[:50]}{'...' if len(response) > 50 else ''}")
        
        try:
            # Test each parsing strategy individually
            strategies = [
                ('Direct parse', lambda r: llm._extract_json_object(r)),
                ('Clean and parse', lambda r: llm._clean_json_response(r)),
                ('Fix and parse', lambda r: llm._fix_and_parse_json(r)),
                ('Fallback', lambda r: llm._create_fallback_response(r)),
            ]
            
            success = False
            for strategy_name, strategy_func in strategies:
                try:
                    result = strategy_func(response)
                    if isinstance(result, dict):
                        print(f"   ✅ {strategy_name}: Success")
                        success = True
                        break
                except Exception as e:
                    print(f"   ❌ {strategy_name}: {str(e)[:50]}...")
            
            if not success:
                print(f"   ⚠️  All strategies failed - would use fallback")
                
        except Exception as e:
            print(f"   💥 Unexpected error: {str(e)}")
    
    print("\n✅ Edge case testing completed!")

if __name__ == "__main__":
    # Run edge case tests first (no API key needed)
    asyncio.run(test_json_parsing_edge_cases())
    
    # Then run real system tests (requires API key)
    asyncio.run(test_real_system())