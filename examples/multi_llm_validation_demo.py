#!/usr/bin/env python3
"""
Multi-LLM Validation Demonstration
=================================

This demo showcases the multi-LLM validation system that uses different
OpenAI models (O3, GPT-4o, GPT-4-turbo) for cross-validation and consensus
building to ensure robust and reliable reasoning results.
"""

import asyncio
import os
import sys
import time

# Add parent directory to path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agentic_reasoning_system import AgenticReasoningSystemSDK


async def demo_multi_llm_validation():
    """Demonstrate multi-LLM validation for reasoning tasks"""
    print("🤖 MULTI-LLM VALIDATION SYSTEM DEMONSTRATION")
    print("=" * 60)
    print("Using O3 (primary), GPT-4o (validation), GPT-4-turbo (testing)")
    print()
    
    # Initialize SDK with multi-LLM validation enabled
    sdk = AgenticReasoningSystemSDK(enable_multi_llm_validation=True)
    
    # Test problems that benefit from cross-validation
    test_problems = [
        {
            "name": "20-Disk Hanoi Validation",
            "problem": """
            Tower of Hanoi with 20 disks: Calculate the minimum number of moves
            required using the mathematical formula. Explain why this represents
            the theoretical complexity limit for reasoning systems.
            """,
            "format": "tower_hanoi",
            "domain": "mathematics",
            "complexity": 5
        },
        {
            "name": "Complex Logical Reasoning",
            "problem": """
            If all quantum computers can solve NP-complete problems efficiently,
            and the Tower of Hanoi is NP-complete, then quantum computers should
            solve 20-disk Hanoi instantly. However, this contradicts the exponential
            nature of the problem. Resolve this apparent paradox.
            """,
            "format": "natural_language",
            "domain": "computer_science",
            "complexity": 4
        },
        {
            "name": "Mathematical Proof Validation",
            "problem": """
            Prove that 2^n - 1 is the minimum number of moves for n-disk Tower of Hanoi.
            Use mathematical induction and explain why no algorithm can do better.
            """,
            "format": "formal_notation",
            "domain": "mathematics",
            "complexity": 4
        }
    ]
    
    for i, test in enumerate(test_problems, 1):
        print(f"{i}. {test['name']}")
        print("-" * 50)
        print(f"Problem: {test['problem'].strip()}")
        print(f"Complexity Level: {test['complexity']}")
        print()
        
        start_time = time.time()
        
        try:
            result = await sdk.reason(
                problem=test["problem"],
                representation_format=test["format"],
                domain=test["domain"],
                complexity_level=test["complexity"],
                requires_causal_analysis=True
            )
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            print(f"📊 PRIMARY RESULT (O3 Model):")
            print(f"   Solution: {result.solution}")
            print(f"   Confidence: {result.confidence:.3f}")
            print(f"   Processing Time: {processing_time:.2f}s")
            
            # Display validation results if available
            if hasattr(result, 'validation_results') and result.validation_results:
                validation = result.validation_results
                print(f"\n🔍 MULTI-LLM VALIDATION:")
                
                if "mathematical_consensus" in validation:
                    # 20-disk Hanoi specific validation
                    print(f"   Mathematical Correctness: {validation['mathematical_consensus']:.2f}")
                    print(f"   Complexity Understanding: {validation['complexity_consensus']:.2f}")
                    print(f"   Recursive Reasoning: {validation['recursive_consensus']:.2f}")
                    print(f"   Overall Consensus: {validation['overall_consensus']:.2f}")
                    print(f"   High Confidence: {validation.get('high_confidence_validation', False)}")
                    
                    # Show individual validator results
                    if validation.get('validation_details'):
                        print(f"\n   📋 Individual Validator Results:")
                        for detail in validation['validation_details']:
                            model = detail.get('validator_model', 'unknown')
                            math_correct = detail.get('mathematical_correctness', False)
                            overall_valid = detail.get('overall_validation', False)
                            print(f"      {model}: Math={math_correct}, Valid={overall_valid}")
                
                elif "consensus_score" in validation:
                    # General validation
                    print(f"   Validation Status: {'✅ VALIDATED' if validation['validated'] else '⚠️ NEEDS REVIEW'}")
                    print(f"   Consensus Score: {validation['consensus_score']:.2f}")
                    print(f"   Validators Used: {len(validation.get('validation_results', []))}")
                    
                    # Show validator agreements
                    for val_result in validation.get('validation_results', []):
                        if 'error' not in val_result:
                            model = val_result.get('validator_model', 'unknown')
                            agrees = val_result.get('agrees_with_solution', False)
                            confidence = val_result.get('confidence_in_assessment', 0)
                            print(f"      {model}: {'✅' if agrees else '❌'} (confidence: {confidence:.2f})")
            else:
                print(f"\n🔍 VALIDATION: Single model result (validation not triggered)")
            
            print(f"\n🧠 TAUTOLOGY COMPLIANCE:")
            print(f"   T1 Overall: {result.tautology_compliance.get('T1_Overall', False)}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "="*60 + "\n")


async def demo_consensus_reasoning():
    """Demonstrate consensus reasoning across multiple LLMs"""
    print("🎯 CONSENSUS REASONING DEMONSTRATION")
    print("=" * 60)
    print("Getting consensus from O3, GPT-4o, and GPT-4-turbo")
    print()
    
    sdk = AgenticReasoningSystemSDK(enable_multi_llm_validation=True)
    
    if not sdk.multi_llm_validator:
        print("❌ Multi-LLM validation not available")
        return
    
    consensus_problem = """
    A 20-disk Tower of Hanoi problem requires 2^20 - 1 moves. If each move
    takes 1 second, how long would it take to solve? Express your answer
    in days, and explain the practical implications for AI reasoning systems.
    """
    
    print("Problem: A 20-disk Tower of Hanoi timing calculation")
    print("-" * 50)
    
    try:
        consensus_result = await sdk.multi_llm_validator.consensus_reasoning(
            consensus_problem, "natural_language", "mathematics"
        )
        
        print(f"📊 CONSENSUS RESULT:")
        print(f"   Solution: {consensus_result.get('solution', 'N/A')}")
        print(f"   Confidence: {consensus_result.get('confidence', 0):.3f}")
        print(f"   Source Model: {consensus_result.get('source_model', 'unknown')}")
        
        if 'consensus_analysis' in consensus_result:
            analysis = consensus_result['consensus_analysis']
            print(f"\n🔍 CONSENSUS ANALYSIS:")
            print(f"   Models Consulted: {analysis['total_models']}")
            print(f"   Confidence Range: {analysis['confidence_range']}")
            print(f"   Agreement Level: {analysis['agreement_level']:.2f}")
            
            print(f"\n📋 ALL MODEL RESULTS:")
            for result in analysis.get('all_results', []):
                model = result.get('source_model', 'unknown')
                solution = result.get('solution', 'N/A')[:100] + "..." if len(result.get('solution', '')) > 100 else result.get('solution', 'N/A')
                confidence = result.get('confidence', 0)
                print(f"   {model}: {solution} (conf: {confidence:.2f})")
        
    except Exception as e:
        print(f"❌ Consensus reasoning failed: {e}")


async def demo_validation_comparison():
    """Compare results with and without multi-LLM validation"""
    print("⚖️ VALIDATION COMPARISON DEMONSTRATION")
    print("=" * 60)
    print("Comparing single-model vs multi-model validation")
    print()
    
    test_problem = """
    Calculate 2^20 - 1 and explain why this number (1,048,575) represents
    the theoretical complexity ceiling for Tower of Hanoi reasoning problems.
    """
    
    # Test without validation
    print("1. Single Model (O3 only):")
    print("-" * 30)
    sdk_single = AgenticReasoningSystemSDK(enable_multi_llm_validation=False)
    
    start_time = time.time()
    result_single = await sdk_single.reason(
        test_problem, "natural_language", "mathematics", complexity_level=4
    )
    single_time = time.time() - start_time
    
    print(f"   Solution: {result_single.solution}")
    print(f"   Confidence: {result_single.confidence:.3f}")
    print(f"   Processing Time: {single_time:.2f}s")
    print(f"   Validation: None")
    
    # Test with validation
    print("\n2. Multi-Model Validation (O3 + GPT-4o + GPT-4-turbo):")
    print("-" * 50)
    sdk_multi = AgenticReasoningSystemSDK(enable_multi_llm_validation=True)
    
    start_time = time.time()
    result_multi = await sdk_multi.reason(
        test_problem, "natural_language", "mathematics", complexity_level=4
    )
    multi_time = time.time() - start_time
    
    print(f"   Solution: {result_multi.solution}")
    print(f"   Confidence: {result_multi.confidence:.3f}")
    print(f"   Processing Time: {multi_time:.2f}s")
    
    if hasattr(result_multi, 'validation_results') and result_multi.validation_results:
        validation = result_multi.validation_results
        print(f"   Validation: {'✅ Validated' if validation.get('validated', False) else '⚠️ Needs Review'}")
        print(f"   Consensus: {validation.get('consensus_score', 0):.2f}")
    else:
        print(f"   Validation: Not triggered")
    
    # Compare results
    print(f"\n📊 COMPARISON:")
    print(f"   Confidence Change: {result_multi.confidence - result_single.confidence:+.3f}")
    print(f"   Time Overhead: {multi_time - single_time:.2f}s ({((multi_time/single_time - 1) * 100):.1f}% increase)")
    print(f"   Validation Benefit: {'High reliability' if hasattr(result_multi, 'validation_results') else 'Standard reliability'}")


async def main():
    """Run all multi-LLM validation demonstrations"""
    print("🤖 MULTI-LLM VALIDATION SYSTEM DEMONSTRATIONS")
    print("=" * 70)
    print("Showcasing cross-validation using O3, GPT-4o, and GPT-4-turbo")
    print("for enhanced reliability and consensus building")
    print()
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return
    
    try:
        await demo_multi_llm_validation()
        await demo_consensus_reasoning()
        await demo_validation_comparison()
        
        print("🎉 MULTI-LLM VALIDATION DEMONSTRATIONS COMPLETED!")
        print("The system has demonstrated enhanced reliability through")
        print("cross-validation and consensus building across multiple models.")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())