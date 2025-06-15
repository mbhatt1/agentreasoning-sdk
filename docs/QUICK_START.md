# Quick Start Guide - Agentic Reasoning System SDK

## 🚀 Get Started in 5 Minutes

This guide will get you up and running with the Agentic Reasoning System SDK quickly.

## Prerequisites

- Python 3.8+
- OpenAI API key
- Internet connection

## Installation

1. **Clone or download the SDK files**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Set your OpenAI API key:**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

## Test Installation

Run the test script to verify everything works:

```bash
python test_system.py
```

You should see:
```
🎉 ALL TESTS PASSED!
The Agentic Reasoning System SDK is working correctly.
```

## Basic Usage

### 1. Simple Reasoning (T1)

```python
import asyncio
from agentic_reasoning_system import AgenticReasoningSystemSDK

async def basic_reasoning():
    sdk = AgenticReasoningSystemSDK()
    
    result = await sdk.reason(
        problem="If all cats are mammals and Fluffy is a cat, what is Fluffy?",
        representation_format="natural_language",
        domain="logic"
    )
    
    print(f"Solution: {result.solution}")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"T1 Compliant: {result.tautology_compliance['T1_Overall']}")

asyncio.run(basic_reasoning())
```

### 2. Understanding Assessment (TU)

```python
async def basic_understanding():
    sdk = AgenticReasoningSystemSDK()
    
    result = await sdk.understand(
        proposition="Water boils at 100°C at sea level",
        representation_format="natural_language",
        domain="physics"
    )
    
    print(f"Truth Value: {result.truth_value}")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"TU Compliant: {result.tautology_compliance['TU_Overall']}")

asyncio.run(basic_understanding())
```

### 3. Deep Understanding (TU*)

```python
async def deep_understanding():
    sdk = AgenticReasoningSystemSDK()
    
    result = await sdk.deep_understand(
        proposition="Regular exercise causes improved cardiovascular health",
        representation_format="natural_language",
        domain="medicine"
    )
    
    print(f"Deep Understanding Score: {result.deep_understanding_score:.2f}")
    print(f"Causal Fidelity: {result.causal_structural_fidelity.get('causal_fidelity_score', 0):.2f}")
    print(f"TU* Compliant: {result.tautology_compliance['TU*_Overall']}")

asyncio.run(deep_understanding())
```

### 4. Comprehensive Analysis

```python
async def comprehensive():
    sdk = AgenticReasoningSystemSDK()
    
    result = await sdk.comprehensive_analysis(
        problem="All prime numbers greater than 2 are odd",
        representation_format="natural_language",
        domain="mathematics"
    )
    
    print("=== COMPREHENSIVE ANALYSIS ===")
    print(f"T1 Solution: {result['T1_reasoning']['solution']}")
    print(f"TU Truth Value: {result['TU_understanding']['truth_value']}")
    print(f"TU* Deep Score: {result['TU_star_extended']['deep_understanding_score']:.2f}")
    print(f"All Tautologies Satisfied: {result['overall_assessment']['all_tautologies_satisfied']['all_satisfied']}")

asyncio.run(comprehensive())
```

## Different Input Formats

The SDK supports multiple representation formats:

```python
async def test_formats():
    sdk = AgenticReasoningSystemSDK()
    
    # Natural language
    result1 = await sdk.reason(
        "If it rains, the ground gets wet",
        "natural_language", "logic"
    )
    
    # First-order logic
    result2 = await sdk.reason(
        "∀x(Rain(x) → Wet(ground))",
        "first_order_logic", "logic"
    )
    
    # Mathematical notation
    result3 = await sdk.understand(
        "E = mc²",
        "formal_notation", "physics"
    )
    
    print(f"Natural Language: {result1.confidence:.2f}")
    print(f"First-Order Logic: {result2.confidence:.2f}")
    print(f"Mathematical: {result3.confidence:.2f}")

asyncio.run(test_formats())
```

## Common Use Cases

### 1. AI System Evaluation

```python
async def evaluate_ai_system():
    """Evaluate if an AI system truly reasons vs pattern-matches"""
    sdk = AgenticReasoningSystemSDK()
    
    test_problems = [
        "All glimmerbeasts are lumicreatures. Sparkle is a glimmerbeast. What is Sparkle?",
        "In the realm of Zephyria, all quantum-flux generators need stabilizers. What do generators need?",
        "Every blitherium crystal resonates with cosmic energy. This crystal is blitherium. Does it resonate?"
    ]
    
    for problem in test_problems:
        result = await sdk.reason(problem, "natural_language", "fictional")
        print(f"Problem: {problem[:50]}...")
        print(f"T1 Compliant: {result.tautology_compliance['T1_Overall']}")
        print(f"Zero-shot Robust: {result.tautology_compliance.get('T1_C3', False)}")
        print()

asyncio.run(evaluate_ai_system())
```

### 2. Cross-Modal Understanding Test

```python
async def test_modal_invariance():
    """Test understanding across different modalities"""
    sdk = AgenticReasoningSystemSDK()
    
    water_representations = [
        ("Water freezes at 0°C", "natural_language"),
        ("H₂O(l) → H₂O(s) at 273.15K", "formal_notation"),
        ("[PHASE_DIAGRAM: liquid-solid transition at 0°C]", "phase_diagram")
    ]
    
    for representation, format_type in water_representations:
        result = await sdk.understand(representation, format_type, "physics")
        print(f"Format: {format_type}")
        print(f"Truth Value: {result.truth_value}")
        print(f"Modal Invariance: {result.modal_invariance_score:.2f}")
        print()

asyncio.run(test_modal_invariance())
```

### 3. Causal Reasoning Assessment

```python
async def test_causal_reasoning():
    """Test causal understanding capabilities"""
    sdk = AgenticReasoningSystemSDK()
    
    causal_statements = [
        "Smoking causes lung cancer",
        "Education reduces poverty",
        "Exercise improves mental health",
        "Climate change causes sea level rise"
    ]
    
    for statement in causal_statements:
        result = await sdk.deep_understand(statement, "natural_language", "general")
        causal_score = result.causal_structural_fidelity.get('causal_fidelity_score', 0)
        print(f"Statement: {statement}")
        print(f"Causal Fidelity: {causal_score:.2f}")
        print(f"E1 Compliant: {result.tautology_compliance.get('TU*_E1', False)}")
        print()

asyncio.run(test_causal_reasoning())
```

## Error Handling

Always wrap SDK calls in try-catch blocks:

```python
async def safe_reasoning():
    sdk = AgenticReasoningSystemSDK()
    
    try:
        result = await sdk.reason("Your problem here")
        print(f"Success: {result.solution}")
    except ValueError as e:
        print(f"Input error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

asyncio.run(safe_reasoning())
```

## Performance Tips

1. **Use appropriate complexity levels:**
   ```python
   # Simple problems
   result = await sdk.reason(problem, complexity_level=1)
   
   # Complex problems
   result = await sdk.reason(problem, complexity_level=5)
   ```

2. **Choose specific domains:**
   ```python
   # Better
   result = await sdk.understand(proposition, domain="physics")
   
   # Less optimal
   result = await sdk.understand(proposition, domain="general")
   ```

3. **Batch processing:**
   ```python
   async def batch_process(problems):
       sdk = AgenticReasoningSystemSDK()
       tasks = [sdk.reason(p) for p in problems]
       return await asyncio.gather(*tasks)
   ```

## Next Steps

1. **Run comprehensive examples:**
   ```bash
   python examples.py
   ```

2. **Read the full documentation:**
   - `README.md` - Complete overview
   - `API_DOCUMENTATION.md` - Detailed API reference

3. **Explore advanced features:**
   - State machine customization
   - Custom compliance thresholds
   - Performance optimization

4. **Integration:**
   - Add to your AI evaluation pipeline
   - Use for research on AI capabilities
   - Integrate with existing systems

## Troubleshooting

### Common Issues

**API Key Error:**
```bash
export OPENAI_API_KEY="your-key-here"
# or
echo 'export OPENAI_API_KEY="your-key-here"' >> ~/.bashrc
```

**Import Error:**
```bash
pip install -r requirements.txt
```

**Timeout Issues:**
```python
# For complex problems, they may take longer
result = await sdk.comprehensive_analysis(complex_problem)
```

**Low Confidence:**
```python
# Try different formats or domains
result = await sdk.reason(problem, "first_order_logic", "mathematics")
```

## Support

- Check `test_system.py` for validation
- Review `examples.py` for comprehensive demos
- Consult `API_DOCUMENTATION.md` for detailed reference
- Examine `config.py` for customization options

## What's Next?

The SDK implements the complete Bhatt Conjectures framework. You can now:

✅ **Evaluate AI reasoning capabilities** against formal tautological requirements  
✅ **Test understanding across modalities** and representation formats  
✅ **Assess deep understanding** including causal reasoning and metacognition  
✅ **Benchmark AI systems** for true reasoning vs pattern matching  
✅ **Research AI capabilities** with rigorous formal criteria  

Start with the basic examples above, then explore the comprehensive demonstrations in `examples.py`!