#!/usr/bin/env python3
"""
Test script to verify JSON parsing fixes
"""

import asyncio
import json
import logging
from agentic_reasoning_system import LLMInterface

# Set up logging to see the debug messages
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_json_parsing_fixes():
    """Test the improved JSON parsing with various problematic responses"""
    
    # Mock LLM interface for testing
    class MockLLMInterface(LLMInterface):
        def __init__(self):
            # Skip the OpenAI client initialization for testing
            self.model = "test"
            
        async def query(self, prompt: str, system_prompt: str = "", temperature: float = 1.0,
                       max_completion_tokens: int = 2000) -> str:
            # Return various problematic JSON responses for testing
            test_responses = [
                # Response 1: Valid JSON
                '{"confidence": 0.8, "solution": "Test solution", "reasoning_steps": ["Step 1", "Step 2"]}',
                
                # Response 2: JSON with extra text
                'Here is the JSON response:\n{"confidence": 0.7, "solution": "Another solution"}',
                
                # Response 3: JSON in code blocks
                '```json\n{"confidence": 0.9, "solution": "Code block solution"}\n```',
                
                # Response 4: Malformed JSON with trailing comma
                '{"confidence": 0.6, "solution": "Trailing comma solution",}',
                
                # Response 5: JSON with unquoted keys
                '{confidence: 0.5, solution: "Unquoted keys"}',
                
                # Response 6: Truncated JSON
                '{"confidence": 0.4, "solution": "Truncated',
                
                # Response 7: Mixed content
                'The analysis shows that {"confidence": 0.3, "solution": "Mixed content"} is the result.',
                
                # Response 8: Single quotes
                "{'confidence': 0.2, 'solution': 'Single quotes'}",
            ]
            
            # Cycle through test responses
            if not hasattr(self, '_response_index'):
                self._response_index = 0
            
            response = test_responses[self._response_index % len(test_responses)]
            self._response_index += 1
            
            logger.info(f"Mock LLM returning: {response}")
            return response
    
    # Create mock interface
    llm = MockLLMInterface()
    
    # Test each scenario
    test_cases = [
        "Valid JSON",
        "JSON with extra text", 
        "JSON in code blocks",
        "Malformed JSON with trailing comma",
        "JSON with unquoted keys",
        "Truncated JSON",
        "Mixed content",
        "Single quotes"
    ]
    
    print("Testing JSON parsing fixes...")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases):
        print(f"\nTest {i+1}: {test_case}")
        print("-" * 30)
        
        try:
            result = await llm.query_json("Test prompt", "Test system prompt")
            print(f"✅ SUCCESS: {result}")
            
            # Verify it's a valid dict with expected fields
            if isinstance(result, dict):
                if 'confidence' in result:
                    print(f"   Confidence: {result['confidence']}")
                if 'solution' in result:
                    print(f"   Solution: {result['solution']}")
                if 'error' in result:
                    print(f"   Error: {result['error']}")
            
        except Exception as e:
            print(f"❌ FAILED: {str(e)}")
    
    print("\n" + "=" * 50)
    print("JSON parsing test completed!")

async def test_fallback_response():
    """Test the fallback response creation"""
    print("\nTesting fallback response creation...")
    print("=" * 50)
    
    # Mock LLM interface
    class MockLLMInterface(LLMInterface):
        def __init__(self):
            self.model = "test"
    
    llm = MockLLMInterface()
    
    # Test various problematic responses
    test_responses = [
        "This is not JSON at all",
        '{"incomplete": "json"',
        "",
        None,
        "confidence: 0.8, solution: some text here",
        'The answer is {"solution": "partial json"} but incomplete'
    ]
    
    for i, response in enumerate(test_responses):
        print(f"\nTest {i+1}: {repr(response)}")
        print("-" * 30)
        
        fallback = llm._create_fallback_response(response or "")
        print(f"✅ Fallback created: {json.dumps(fallback, indent=2)}")

if __name__ == "__main__":
    asyncio.run(test_json_parsing_fixes())
    asyncio.run(test_fallback_response())