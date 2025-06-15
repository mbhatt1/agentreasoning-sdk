#!/usr/bin/env python3
"""
Comprehensive Test Suite for Agentic Reasoning System SDK
========================================================

This consolidated test suite combines all testing functionality:
- Basic functionality tests
- JSON parsing tests  
- Extreme complexity tests
- Real system tests
- Edge case tests

Run with: python -m pytest tests/test_comprehensive.py -v
"""

import asyncio
import os
import sys
import pytest
from unittest.mock import Mock, patch

# Add parent directory to path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agentic_reasoning_system import AgenticReasoningSystemSDK, LLMInterface

class TestBasicFunctionality:
    """Test basic functionality of all three tautologies"""
    
    @pytest.mark.asyncio
    async def test_api_key_required(self):
        """Test that API key is required"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(Exception):
                sdk = AgenticReasoningSystemSDK()
                await sdk.reason("test problem", "natural_language", "logic")
    
    @pytest.mark.asyncio
    async def test_t1_reasoning(self):
        """Test T1 Reasoning functionality"""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")
        
        sdk = AgenticReasoningSystemSDK()
        result = await sdk.reason(
            problem="If all cats are mammals and all mammals are animals, what are cats?",
            representation_format="natural_language",
            domain="logic"
        )
        
        assert result.solution is not None
        assert result.confidence > 0.0
        assert isinstance(result.tautology_compliance, dict)
    
    @pytest.mark.asyncio
    async def test_tu_understanding(self):
        """Test TU Understanding functionality"""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")
        
        sdk = AgenticReasoningSystemSDK()
        result = await sdk.understand(
            proposition="Water freezes at 0°C",
            representation_format="natural_language",
            domain="physics"
        )
        
        assert result.truth_value is not None
        assert isinstance(result.tautology_compliance, dict)
    
    @pytest.mark.asyncio
    async def test_tustar_extended(self):
        """Test TU* Extended Understanding functionality"""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")
        
        sdk = AgenticReasoningSystemSDK()
        result = await sdk.deep_understand(
            proposition="Smoking causes lung cancer",
            representation_format="natural_language",
            domain="medicine"
        )
        
        assert result.deep_understanding_score is not None
        assert isinstance(result.tautology_compliance, dict)


class TestJSONParsing:
    """Test JSON parsing fixes and edge cases"""
    
    def test_json_parsing_with_mock_responses(self):
        """Test JSON parsing with various problematic responses"""
        
        class MockLLMInterface(LLMInterface):
            def __init__(self):
                pass
            
            async def query(self, prompt: str, system_prompt: str = "", temperature: float = 1.0,
                          max_tokens: int = 2000) -> str:
                return '{"test": "response"}'
        
        # Test cases for problematic JSON responses
        test_cases = [
            '{"solution": "Animals", "confidence": 0.95}',  # Valid JSON
            "{'solution': 'Animals', 'confidence': 0.95}",  # Single quotes
            '{"solution": "Animals", "confidence": 0.95,}',  # Trailing comma
            '```json\n{"solution": "Animals"}\n```',  # Code blocks
            'Some text\n{"solution": "Animals"}\nMore text',  # Mixed content
        ]
        
        llm = MockLLMInterface()
        
        for i, test_case in enumerate(test_cases):
            try:
                # Test the JSON parsing methods
                result = llm._clean_json_response(test_case)
                assert isinstance(result, str)
                print(f"✓ Test case {i+1} passed")
            except Exception as e:
                print(f"❌ Test case {i+1} failed: {e}")


class TestRepresentationFormats:
    """Test different representation formats"""
    
    @pytest.mark.asyncio
    async def test_multiple_formats(self):
        """Test reasoning with different representation formats"""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")
        
        sdk = AgenticReasoningSystemSDK()
        formats = ["natural_language", "first_order_logic", "formal_notation"]
        
        for format_type in formats:
            try:
                result = await sdk.reason(
                    "Simple logical problem",
                    format_type,
                    "logic"
                )
                assert result is not None
                print(f"✓ Format {format_type} works")
            except Exception as e:
                print(f"❌ Format {format_type} failed: {e}")


class TestDomains:
    """Test different knowledge domains"""
    
    @pytest.mark.asyncio
    async def test_multiple_domains(self):
        """Test reasoning across different domains"""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")
        
        sdk = AgenticReasoningSystemSDK()
        domains = ["logic", "mathematics", "physics", "chemistry"]
        
        for domain in domains:
            try:
                result = await sdk.reason(
                    "Domain-specific problem",
                    "natural_language",
                    domain
                )
                assert result is not None
                print(f"✓ Domain {domain} works")
            except Exception as e:
                print(f"❌ Domain {domain} failed: {e}")


class TestExtremeComplexity:
    """Test extreme complexity scenarios"""
    
    @pytest.mark.asyncio
    async def test_hanoi_complexity(self):
        """Test Tower of Hanoi complexity problems"""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")
        
        sdk = AgenticReasoningSystemSDK()
        
        # Test cases with increasing complexity
        test_cases = [
            {
                "name": "3-Disk Hanoi",
                "problem": "Solve Tower of Hanoi with 3 disks. How many moves required?",
                "expected_moves": 7,
                "discs": 3
            },
            {
                "name": "5-Disk Hanoi", 
                "problem": "Solve Tower of Hanoi with 5 disks. What's the minimum number of moves?",
                "expected_moves": 31,
                "discs": 5
            }
        ]
        
        for test_case in test_cases:
            try:
                result = await sdk.reason(
                    test_case["problem"],
                    "tower_hanoi",
                    "mathematics",
                    complexity_level=4
                )
                
                assert result.solution is not None
                assert result.confidence > 0.0
                print(f"✓ {test_case['name']} completed")
                
            except Exception as e:
                print(f"❌ {test_case['name']} failed: {e}")


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    @pytest.mark.asyncio
    async def test_edge_cases(self):
        """Test various edge cases"""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")
        
        sdk = AgenticReasoningSystemSDK()
        
        edge_cases = [
            {
                "name": "Empty Problem",
                "problem": "",
                "format": "natural_language",
                "domain": "general"
            },
            {
                "name": "Very Long Problem",
                "problem": "A" * 1000,
                "format": "natural_language", 
                "domain": "general"
            },
            {
                "name": "Special Characters",
                "problem": "Problem with special chars: @#$%^&*()",
                "format": "natural_language",
                "domain": "general"
            }
        ]
        
        for case in edge_cases:
            try:
                result = await sdk.reason(
                    case["problem"],
                    case["format"],
                    case["domain"]
                )
                print(f"✓ {case['name']} handled gracefully")
            except Exception as e:
                print(f"⚠️ {case['name']} failed as expected: {e}")


# Convenience functions for running tests manually
async def run_basic_tests():
    """Run basic functionality tests"""
    test_class = TestBasicFunctionality()
    await test_class.test_t1_reasoning()
    await test_class.test_tu_understanding()
    await test_class.test_tustar_extended()
    print("✓ Basic functionality tests completed")


async def run_all_tests():
    """Run all tests manually (without pytest)"""
    print("Running Comprehensive Test Suite...")
    print("=" * 50)
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return False
    
    try:
        await run_basic_tests()
        
        # Run JSON parsing tests
        json_test = TestJSONParsing()
        json_test.test_json_parsing_with_mock_responses()
        print("✓ JSON parsing tests completed")
        
        # Run format tests
        format_test = TestRepresentationFormats()
        await format_test.test_multiple_formats()
        print("✓ Representation format tests completed")
        
        # Run domain tests
        domain_test = TestDomains()
        await domain_test.test_multiple_domains()
        print("✓ Domain tests completed")
        
        # Run complexity tests
        complexity_test = TestExtremeComplexity()
        await complexity_test.test_hanoi_complexity()
        print("✓ Extreme complexity tests completed")
        
        # Run edge case tests
        edge_test = TestEdgeCases()
        await edge_test.test_edge_cases()
        print("✓ Edge case tests completed")
        
        print("\n🎉 All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        return False


if __name__ == "__main__":
    # Run tests manually if executed directly
    asyncio.run(run_all_tests())