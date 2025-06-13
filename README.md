# Agentic Reasoning System SDK

An implementation of the **Bhatt Conjectures** framework for evaluating AI reasoning and understanding capabilities. This SDK provides a comprehensive system that uses OpenAI's LLMs to implement the three core tautologies from the research paper.

## Overview

The Bhatt Conjectures define three tautological benchmarks for AI capabilities:

- **T1**: Reasoning-Capability Tautology
- **TU**: Understanding-Capability Tautology  
- **TU***: Extended Understanding-Capability Tautology

This SDK implements all three tautologies using a state machine architecture with OpenAI's language models handling all reasoning, parsing, and understanding tasks.

## Features

### T1 Reasoning-Capability Tautology
- **Representation Invariance (C1)**: Works across different input formats (natural language, formal logic, lambda calculus, etc.)
- **Complexity Scaling (C2)**: Handles increased problem complexity
- **Zero-Shot Robustness (C3)**: Processes novel surface patterns not seen in training

### TU Understanding-Capability Tautology
- **Modal Invariance (C4)**: Understanding survives cross-modal transfer
- **Counterfactual Competence (C5)**: Answers derived queries and handles hypotheticals
- **Distribution Shift (C6)**: Stable truth evaluations with rare/synthetic examples

### TU* Extended Understanding-Capability Tautology
- **Causal Structural Fidelity (E1)**: Internal representation mirrors causal graphs, enables do-calculus
- **Metacognitive Self-Awareness (E2)**: Evaluates and calibrates its own inference reliability
- **Phenomenal Awareness (E3)**: Theoretical assessment of subjective experience (untestable boundary)

## Installation

```bash
pip install openai asyncio
```

Set your OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

## Quick Start

```python
import asyncio
from agentic_reasoning_system import AgenticReasoningSystemSDK

async def main():
    # Initialize the SDK
    sdk = AgenticReasoningSystemSDK()
    
    # T1 Reasoning
    reasoning_result = await sdk.reason(
        problem="If all swans are birds and all birds can fly, what can we conclude about swans?",
        representation_format="natural_language",
        domain="logic"
    )
    print(f"Solution: {reasoning_result.solution}")
    print(f"T1 Compliance: {reasoning_result.tautology_compliance}")
    
    # TU Understanding
    understanding_result = await sdk.understand(
        proposition="Water freezes at 0°C",
        representation_format="natural_language",
        domain="physics"
    )
    print(f"Truth Value: {understanding_result.truth_value}")
    print(f"TU Compliance: {understanding_result.tautology_compliance}")
    
    # TU* Extended Understanding
    extended_result = await sdk.deep_understand(
        proposition="Increasing temperature causes ice to melt",
        representation_format="natural_language",
        domain="physics"
    )
    print(f"Deep Understanding Score: {extended_result.deep_understanding_score}")
    print(f"TU* Compliance: {extended_result.tautology_compliance}")
    
    # Comprehensive Analysis
    comprehensive_result = await sdk.comprehensive_analysis(
        problem="All ravens are black. This bird is a raven. What color is this bird?",
        representation_format="natural_language",
        domain="logic"
    )
    print(f"Overall Assessment: {comprehensive_result['overall_assessment']}")

if __name__ == "__main__":
    asyncio.run(main())
```

## API Reference

### AgenticReasoningSystemSDK

The main SDK class that provides access to all three tautology implementations.

#### Methods

##### `reason(problem, representation_format, domain, complexity_level, requires_causal_analysis)`
Performs T1 reasoning on a problem.

**Parameters:**
- `problem` (str): The problem to solve
- `representation_format` (str): Format of the problem (default: "natural_language")
  - Supported formats: "natural_language", "first_order_logic", "lambda_calculus", "sudoku_constraints", "tower_hanoi", "phase_diagram", "iupac_string", "image_schema", "braille", "speech", "formal_notation"
- `domain` (str): Domain of the problem (default: "general")
- `complexity_level` (int): Complexity level 1-5 (default: 3)
- `requires_causal_analysis` (bool): Whether causal analysis is needed (default: False)

**Returns:** `ReasoningResult`

##### `understand(proposition, representation_format, domain)`
Performs TU understanding of a proposition.

**Parameters:**
- `proposition` (str): The proposition to understand
- `representation_format` (str): Format of the proposition (default: "natural_language")
- `domain` (str): Domain of the proposition (default: "general")

**Returns:** `UnderstandingResult`

##### `deep_understand(proposition, representation_format, domain)`
Performs TU* extended understanding of a proposition.

**Parameters:**
- `proposition` (str): The proposition to deeply understand
- `representation_format` (str): Format of the proposition (default: "natural_language")
- `domain` (str): Domain of the proposition (default: "general")

**Returns:** `ExtendedUnderstandingResult`

##### `comprehensive_analysis(problem, representation_format, domain)`
Performs comprehensive analysis using all three tautologies.

**Parameters:**
- `problem` (str): The problem/proposition to analyze
- `representation_format` (str): Format of the input (default: "natural_language")
- `domain` (str): Domain of the problem (default: "general")

**Returns:** `Dict[str, Any]` containing results from all three tautology assessments

## State Machine Architecture

The system uses a state machine to coordinate the reasoning process:

1. **IDLE** → **PARSING_INPUT** → **REPRESENTATION_MAPPING**
2. **FAST_PROCESSING** ↔ **SLOW_PROCESSING**
3. **METACOGNITIVE_EVALUATION** → **CAUSAL_ANALYSIS**
4. **GENERATING_RESPONSE** → **SELF_VERIFICATION** → **COMPLETE**

The state machine automatically determines the optimal path based on problem complexity, confidence levels, and requirements.

## Supported Representation Formats

- **natural_language**: Standard text problems
- **first_order_logic**: Formal logical expressions
- **lambda_calculus**: Lambda calculus expressions
- **sudoku_constraints**: Sudoku puzzle constraints
- **tower_hanoi**: Tower of Hanoi problems
- **phase_diagram**: Phase diagram representations
- **iupac_string**: Chemical IUPAC notation
- **image_schema**: Visual schema representations
- **braille**: Braille text representations
- **speech**: Speech/audio representations
- **formal_notation**: Mathematical notation

## Tautology Compliance

Each method returns compliance assessments for the relevant tautology requirements:

### T1 Compliance
- `T1_R1`: Correct solution from any logically equivalent representation
- `T1_R2`: High success probability with out-of-distribution surface forms
- `T1_C1`: Representation invariance
- `T1_C2`: Complexity scaling
- `T1_C3`: Zero-shot robustness

### TU Compliance
- `TU_U1`: Truth-preserving representation mapping
- `TU_U2`: Performance with statistically independent data
- `TU_C4`: Modal invariance
- `TU_C5`: Counterfactual competence
- `TU_C6`: Distribution shift robustness

### TU* Compliance
- All TU requirements plus:
- `TU*_E1`: Causal structural fidelity
- `TU*_E2`: Metacognitive self-awareness
- `TU*_E3`: Phenomenal awareness (theoretical)

## Examples

### Different Representation Formats

```python
# Natural language
result = await sdk.reason(
    "If it rains, the ground gets wet. It's raining. Is the ground wet?",
    "natural_language", "logic"
)

# First-order logic
result = await sdk.reason(
    "∀x(Rain(x) → Wet(ground)) ∧ Rain(now) → ?",
    "first_order_logic", "logic"
)

# Lambda calculus
result = await sdk.reason(
    "λx.λy.(x → y) rain wet",
    "lambda_calculus", "logic"
)
```

### Domain-Specific Problems

```python
# Mathematics
result = await sdk.reason(
    "Solve: 2x + 3 = 7",
    "natural_language", "mathematics"
)

# Physics
result = await sdk.understand(
    "F = ma",
    "formal_notation", "physics"
)

# Chemistry
result = await sdk.deep_understand(
    "2-methylpropanoic acid",
    "iupac_string", "chemistry"
)
```

### Causal Reasoning

```python
result = await sdk.deep_understand(
    "Smoking causes lung cancer",
    "natural_language", "medicine"
)

# Check causal fidelity
causal_quality = result.causal_structural_fidelity['causal_fidelity_score']
```

## Error Handling

The SDK includes comprehensive error handling:

```python
try:
    result = await sdk.reason(problem, format, domain)
    if result.tautology_compliance['T1_Overall']:
        print("T1 requirements satisfied!")
    else:
        print("T1 requirements not met:", result.tautology_compliance)
except Exception as e:
    print(f"Reasoning failed: {e}")
```

## Performance Considerations

- **Fast vs Slow Processing**: The system automatically chooses between fast intuitive processing and slow deliberative processing based on problem complexity and confidence levels.
- **Async Operations**: All operations are asynchronous for better performance.
- **Token Usage**: Complex analyses may use significant OpenAI API tokens.

## Research Applications

This SDK is designed for:

- **AI Capability Assessment**: Evaluate whether AI systems truly reason vs. pattern-match
- **Benchmark Development**: Create rigorous tests for AI reasoning capabilities
- **Research**: Study the boundaries between reasoning, understanding, and consciousness
- **System Evaluation**: Assess AI systems against formal tautological requirements

## Limitations

- **LLM Dependency**: All reasoning depends on OpenAI's language models
- **Phenomenal Awareness**: E3 requirement is acknowledged as currently untestable
- **API Costs**: Comprehensive analyses can be expensive due to multiple LLM calls
- **Async Requirement**: All operations must be run in async context

## Contributing

This implementation follows the formal definitions from the Bhatt Conjectures paper. Contributions should maintain compliance with the tautological requirements while improving practical usability.

## License

MIT License - See LICENSE file for details.

## Citation

If you use this SDK in research, please cite the original Bhatt Conjectures paper:

```
Bhatt, M. (2025). Bhatt Conjectures: On Necessary-But-Not-Sufficient Benchmark Tautology for Human Like Reasoning.
```

## Support

For issues, questions, or contributions, please refer to the project repository.