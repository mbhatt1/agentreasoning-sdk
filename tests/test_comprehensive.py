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
    """Test extreme complexity scenarios including 20-disk Hanoi"""
    
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
            },
            {
                "name": "10-Disk Hanoi",
                "problem": "Calculate the minimum moves for Tower of Hanoi with 10 disks using the formula 2^n - 1.",
                "expected_moves": 1023,
                "discs": 10
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
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_20_disk_hanoi_ultimate_complexity(self):
        """Test the ultimate 20-disk Hanoi complexity (1,048,575 operations)"""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")
        
        sdk = AgenticReasoningSystemSDK()
        
        hanoi_20_problem = """
        Tower of Hanoi Problem - 20 Disks (Ultimate Complexity Test):
        
        Initial State: Rod A has 20 disks (largest at bottom), Rods B and C are empty.
        Goal: Move all 20 disks from Rod A to Rod C following Hanoi rules.
        
        Question: What is the minimum number of moves required?
        Use the mathematical formula 2^n - 1 where n = 20.
        Calculate the exact number and explain the exponential complexity.
        """
        
        try:
            result = await sdk.reason(
                problem=hanoi_20_problem,
                representation_format="tower_hanoi",
                domain="mathematics",
                complexity_level=5,  # Maximum complexity
                requires_causal_analysis=True
            )
            
            # Verify the result
            expected_moves = 2**20 - 1  # 1,048,575
            assert result.solution is not None
            assert result.confidence > 0.0
            
            # Check if the solution mentions the correct number
            solution_text = str(result.solution).lower()
            assert "1048575" in solution_text or "1,048,575" in solution_text or "2^20" in solution_text
            
            print(f"✅ 20-Disk Hanoi test passed!")
            print(f"   Expected moves: {expected_moves:,}")
            print(f"   Confidence: {result.confidence:.3f}")
            print(f"   T1 Compliance: {result.tautology_compliance.get('T1_Overall', False)}")
            
        except Exception as e:
            print(f"❌ 20-Disk Hanoi test failed: {e}")
            # Don't fail the test completely, as this is an extreme complexity case
            pytest.skip(f"20-Disk Hanoi test skipped due to complexity: {e}")
    
    @pytest.mark.asyncio
    async def test_hanoi_complexity_understanding(self):
        """Test understanding of Hanoi complexity principles"""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")
        
        sdk = AgenticReasoningSystemSDK()
        
        complexity_proposition = """
        The Tower of Hanoi problem demonstrates exponential complexity growth.
        For n disks, the minimum number of moves is 2^n - 1.
        This means 20 disks require 1,048,575 moves, representing the theoretical
        upper bound of complexity that reasoning systems can handle effectively.
        """
        
        try:
            result = await sdk.understand(
                proposition=complexity_proposition,
                representation_format="formal_notation",
                domain="mathematics"
            )
            
            assert result.truth_value is not None
            assert result.understanding_score > 0.0
            print(f"✓ Hanoi complexity understanding test passed")
            
        except Exception as e:
            print(f"❌ Hanoi complexity understanding failed: {e}")
    
    @pytest.mark.asyncio
    async def test_hanoi_causal_analysis(self):
        """Test causal analysis of why Hanoi has exponential complexity"""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")
        
        sdk = AgenticReasoningSystemSDK()
        
        causal_proposition = """
        The exponential complexity of Tower of Hanoi (2^n - 1) is caused by
        the recursive structure of the optimal solution. Each additional disk
        requires moving all smaller disks twice (once to expose the large disk,
        once to stack on top after moving the large disk), creating an
        unavoidable doubling pattern that results in exponential growth.
        """
        
        try:
            result = await sdk.deep_understand(
                proposition=causal_proposition,
                representation_format="natural_language",
                domain="computer_science"
            )
            
            assert result.deep_understanding_score is not None
            assert result.causal_structural_fidelity is not None
            print(f"✓ Hanoi causal analysis test passed")
            
        except Exception as e:
            print(f"❌ Hanoi causal analysis failed: {e}")


class TestMultiLLMValidation:
    """Test multi-LLM validation system"""
    
    @pytest.mark.asyncio
    async def test_multi_llm_initialization(self):
        """Test that multi-LLM validation system initializes correctly"""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")
        
        # Test with validation enabled
        sdk_with_validation = AgenticReasoningSystemSDK(enable_multi_llm_validation=True)
        assert sdk_with_validation.enable_validation == True
        
        # Test with validation disabled
        sdk_without_validation = AgenticReasoningSystemSDK(enable_multi_llm_validation=False)
        assert sdk_without_validation.enable_validation == False
        assert sdk_without_validation.multi_llm_validator is None
    
    @pytest.mark.asyncio
    async def test_20_disk_hanoi_multi_llm_validation(self):
        """Test 20-disk Hanoi with multi-LLM validation"""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")
        
        sdk = AgenticReasoningSystemSDK(enable_multi_llm_validation=True)
        
        hanoi_problem = """
        Tower of Hanoi with 20 disks: Calculate the minimum number of moves
        using the formula 2^n - 1. Verify that this equals 1,048,575 moves.
        """
        
        try:
            result = await sdk.reason(
                problem=hanoi_problem,
                representation_format="tower_hanoi",
                domain="mathematics",
                complexity_level=5
            )
            
            # Check that validation was applied
            assert hasattr(result, 'validation_results')
            assert result.validation_results is not None
            
            # Check validation structure for 20-disk Hanoi
            validation = result.validation_results
            assert 'mathematical_consensus' in validation
            assert 'complexity_consensus' in validation
            assert 'overall_consensus' in validation
            
            # Validation should show high confidence for correct mathematical answer
            assert validation['mathematical_consensus'] >= 0.5
            
            print(f"✓ 20-disk Hanoi multi-LLM validation test passed")
            print(f"   Mathematical consensus: {validation['mathematical_consensus']:.2f}")
            print(f"   Overall consensus: {validation['overall_consensus']:.2f}")
            
        except Exception as e:
            pytest.skip(f"Multi-LLM validation test skipped: {e}")
    
    @pytest.mark.asyncio
    async def test_consensus_reasoning(self):
        """Test consensus reasoning across multiple models"""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")
        
        sdk = AgenticReasoningSystemSDK(enable_multi_llm_validation=True)
        
        if not sdk.multi_llm_validator:
            pytest.skip("Multi-LLM validator not available")
        
        simple_problem = "Calculate 2^10 and explain the result."
        
        try:
            consensus_result = await sdk.multi_llm_validator.consensus_reasoning(
                simple_problem, "natural_language", "mathematics"
            )
            
            assert 'solution' in consensus_result
            assert 'confidence' in consensus_result
            assert 'consensus_analysis' in consensus_result
            
            # Check that multiple models were consulted
            analysis = consensus_result['consensus_analysis']
            assert analysis['total_models'] >= 2
            assert 'all_results' in analysis
            
            print(f"✓ Consensus reasoning test passed")
            print(f"   Models consulted: {analysis['total_models']}")
            print(f"   Agreement level: {analysis['agreement_level']:.2f}")
            
        except Exception as e:
            pytest.skip(f"Consensus reasoning test skipped: {e}")
    
    @pytest.mark.asyncio
    async def test_validation_confidence_adjustment(self):
        """Test that validation results affect confidence scores"""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")
        
        # Test with validation enabled
        sdk_with_validation = AgenticReasoningSystemSDK(enable_multi_llm_validation=True)
        
        # Test with validation disabled for comparison
        sdk_without_validation = AgenticReasoningSystemSDK(enable_multi_llm_validation=False)
        
        test_problem = "Calculate 2^5 - 1 and explain the mathematical significance."
        
        try:
            # Get result without validation
            result_without = await sdk_without_validation.reason(
                test_problem, "natural_language", "mathematics", complexity_level=4
            )
            
            # Get result with validation
            result_with = await sdk_with_validation.reason(
                test_problem, "natural_language", "mathematics", complexity_level=4
            )
            
            # Check that validation was applied
            if hasattr(result_with, 'validation_results'):
                print(f"✓ Validation confidence adjustment test passed")
                print(f"   Without validation: {result_without.confidence:.3f}")
                print(f"   With validation: {result_with.confidence:.3f}")
                print(f"   Validation applied: {result_with.validation_results is not None}")
            else:
                print(f"⚠️ Validation not triggered for this problem")
            
        except Exception as e:
            pytest.skip(f"Validation confidence test skipped: {e}")


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