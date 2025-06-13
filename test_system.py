#!/usr/bin/env python3
"""
Test script for the Agentic Reasoning System SDK
===============================================

This script provides basic tests to verify the system is working correctly.
Run this after setting up your OpenAI API key to validate the installation.
"""

import asyncio
import os
import sys
from agentic_reasoning_system import AgenticReasoningSystemSDK

async def test_basic_functionality():
    """Test basic functionality of all three tautologies"""
    print("Testing Agentic Reasoning System SDK...")
    print("=" * 50)
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return False
    
    try:
        # Initialize SDK
        sdk = AgenticReasoningSystemSDK()
        print("✓ SDK initialized successfully")
        
        # Test T1 Reasoning
        print("\n1. Testing T1 Reasoning...")
        reasoning_result = await sdk.reason(
            problem="If all cats are mammals and all mammals are animals, what are cats?",
            representation_format="natural_language",
            domain="logic"
        )
        
        print(f"   Solution: {reasoning_result.solution}")
        print(f"   Confidence: {reasoning_result.confidence:.2f}")
        print(f"   T1 Compliance: {reasoning_result.tautology_compliance.get('T1_Overall', False)}")
        
        if reasoning_result.solution and reasoning_result.confidence > 0.5:
            print("   ✓ T1 Reasoning test passed")
        else:
            print("   ❌ T1 Reasoning test failed")
            return False
        
        # Test TU Understanding
        print("\n2. Testing TU Understanding...")
        understanding_result = await sdk.understand(
            proposition="The sun rises in the east",
            representation_format="natural_language",
            domain="astronomy"
        )
        
        print(f"   Truth Value: {understanding_result.truth_value}")
        print(f"   Confidence: {understanding_result.confidence:.2f}")
        print(f"   TU Compliance: {understanding_result.tautology_compliance.get('TU_Overall', False)}")
        
        if understanding_result.confidence > 0.5:
            print("   ✓ TU Understanding test passed")
        else:
            print("   ❌ TU Understanding test failed")
            return False
        
        # Test TU* Extended Understanding
        print("\n3. Testing TU* Extended Understanding...")
        extended_result = await sdk.deep_understand(
            proposition="Exercise improves cardiovascular health",
            representation_format="natural_language",
            domain="medicine"
        )
        
        print(f"   Deep Understanding Score: {extended_result.deep_understanding_score:.2f}")
        print(f"   TU* Compliance: {extended_result.tautology_compliance.get('TU*_Overall', False)}")
        
        if extended_result.deep_understanding_score > 0.3:
            print("   ✓ TU* Extended Understanding test passed")
        else:
            print("   ❌ TU* Extended Understanding test failed")
            return False
        
        # Test Comprehensive Analysis
        print("\n4. Testing Comprehensive Analysis...")
        comprehensive_result = await sdk.comprehensive_analysis(
            problem="All squares are rectangles. This shape is a square. What type of shape is it?",
            representation_format="natural_language",
            domain="geometry"
        )
        
        overall_success = comprehensive_result['overall_assessment']['all_tautologies_satisfied']['all_satisfied']
        print(f"   All Tautologies Satisfied: {overall_success}")
        print(f"   Overall Capability: {comprehensive_result['overall_assessment']['system_capabilities']['overall_capability']:.2f}")
        
        if comprehensive_result['T1_reasoning']['solution']:
            print("   ✓ Comprehensive Analysis test passed")
        else:
            print("   ❌ Comprehensive Analysis test failed")
            return False
        
        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED!")
        print("The Agentic Reasoning System SDK is working correctly.")
        print("\nSystem Capabilities Summary:")
        print(f"- T1 Reasoning: {reasoning_result.confidence:.1%}")
        print(f"- TU Understanding: {understanding_result.confidence:.1%}")
        print(f"- TU* Extended Understanding: {extended_result.deep_understanding_score:.1%}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        print("\nPossible issues:")
        print("1. Check your OpenAI API key is valid")
        print("2. Ensure you have internet connectivity")
        print("3. Verify all dependencies are installed")
        return False

async def test_representation_formats():
    """Test different representation formats"""
    print("\n" + "=" * 50)
    print("Testing Different Representation Formats...")
    print("=" * 50)
    
    sdk = AgenticReasoningSystemSDK()
    
    test_cases = [
        ("All birds can fly", "natural_language"),
        ("∀x(Bird(x) → CanFly(x))", "first_order_logic"),
        ("H₂O → ice at T < 0°C", "formal_notation")
    ]
    
    for i, (problem, format_type) in enumerate(test_cases, 1):
        print(f"\n{i}. Testing {format_type}:")
        print(f"   Input: {problem}")
        
        try:
            result = await sdk.reason(problem, format_type, "logic")
            print(f"   Output: {result.solution}")
            print(f"   Confidence: {result.confidence:.2f}")
            print("   ✓ Format test passed")
        except Exception as e:
            print(f"   ❌ Format test failed: {str(e)}")

async def test_domains():
    """Test different knowledge domains"""
    print("\n" + "=" * 50)
    print("Testing Different Knowledge Domains...")
    print("=" * 50)
    
    sdk = AgenticReasoningSystemSDK()
    
    domain_tests = [
        ("2 + 2 = 4", "mathematics"),
        ("F = ma", "physics"),
        ("DNA contains genetic information", "biology"),
        ("Supply and demand affect prices", "economics")
    ]
    
    for i, (proposition, domain) in enumerate(domain_tests, 1):
        print(f"\n{i}. Testing {domain}:")
        print(f"   Proposition: {proposition}")
        
        try:
            result = await sdk.understand(proposition, "natural_language", domain)
            print(f"   Truth Value: {result.truth_value}")
            print(f"   Confidence: {result.confidence:.2f}")
            print("   ✓ Domain test passed")
        except Exception as e:
            print(f"   ❌ Domain test failed: {str(e)}")

async def test_state_machine():
    """Test state machine transitions"""
    print("\n" + "=" * 50)
    print("Testing State Machine Transitions...")
    print("=" * 50)
    
    sdk = AgenticReasoningSystemSDK()
    
    # Test with different complexity levels
    complexity_tests = [
        ("Simple: 1 + 1 = ?", 1),
        ("Medium: Solve for x: 2x + 3 = 7", 3),
        ("Complex: Prove that the square root of 2 is irrational", 5)
    ]
    
    for i, (problem, complexity) in enumerate(complexity_tests, 1):
        print(f"\n{i}. Testing complexity level {complexity}:")
        print(f"   Problem: {problem}")
        
        try:
            result = await sdk.reason(problem, "natural_language", "mathematics", complexity)
            print(f"   State Transitions: {len(result.state_transitions)}")
            print(f"   Final State: {result.state_transitions[-1] if result.state_transitions else 'None'}")
            print(f"   Time Taken: {result.time_taken:.2f}s")
            print("   ✓ State machine test passed")
        except Exception as e:
            print(f"   ❌ State machine test failed: {str(e)}")

async def main():
    """Run all tests"""
    print("AGENTIC REASONING SYSTEM SDK - TEST SUITE")
    print("=" * 50)
    print("This test suite validates the SDK functionality.")
    print("Ensure your OPENAI_API_KEY is set before running.\n")
    
    # Run basic functionality tests
    basic_success = await test_basic_functionality()
    
    if basic_success:
        # Run additional tests
        await test_representation_formats()
        await test_domains()
        await test_state_machine()
        
        print("\n" + "=" * 50)
        print("🎉 ALL TESTS COMPLETED!")
        print("=" * 50)
        print("\nThe SDK is ready for use. Try running:")
        print("python examples.py")
        print("\nFor comprehensive examples and demonstrations.")
    else:
        print("\n" + "=" * 50)
        print("❌ BASIC TESTS FAILED")
        print("=" * 50)
        print("Please fix the issues above before proceeding.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())