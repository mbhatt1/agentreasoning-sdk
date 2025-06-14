# Agentic Reasoning System SDK - API Documentation

## Table of Contents
1. [Overview](#overview)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Core Classes](#core-classes)
5. [Methods](#methods)
6. [Data Structures](#data-structures)
7. [Configuration](#configuration)
8. [Error Handling](#error-handling)
9. [Examples](#examples)
10. [Advanced Usage](#advanced-usage)

## Overview

The Agentic Reasoning System SDK implements the Bhatt Conjectures framework for evaluating AI reasoning and understanding capabilities. It provides three main tautological assessments:

- **T1**: Reasoning-Capability Tautology
- **TU**: Understanding-Capability Tautology
- **TU***: Extended Understanding-Capability Tautology

## Installation

```bash
pip install -r requirements.txt
export OPENAI_API_KEY="your-openai-api-key"
```

## Quick Start

```python
import asyncio
from agentic_reasoning_system import AgenticReasoningSystemSDK

async def main():
    sdk = AgenticReasoningSystemSDK()
    
    # T1 Reasoning
    result = await sdk.reason("If A then B. A is true. What about B?")
    print(f"Solution: {result.solution}")
    
    # TU Understanding
    understanding = await sdk.understand("Water boils at 100°C")
    print(f"Truth value: {understanding.truth_value}")
    
    # TU* Extended Understanding
    deep = await sdk.deep_understand("Exercise causes improved health")
    print(f"Deep understanding score: {deep.deep_understanding_score}")

asyncio.run(main())
```

## Core Classes

### AgenticReasoningSystemSDK

The main SDK class that provides access to all tautology implementations.

```python
class AgenticReasoningSystemSDK:
    def __init__(self, openai_api_key: Optional[str] = None, model: str = "gpt-4.1-nano")
```

**Parameters:**
- `openai_api_key`: OpenAI API key (optional, can use environment variable)
- `model`: OpenAI model to use (default: "gpt-4.1-nano")

### LLMInterface

Interface to OpenAI's language models.

```python
class LLMInterface:
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4.1-nano")
    async def query(self, prompt: str, system_prompt: str = "", temperature: float = 1.0, max_completion_tokens: int = 2000) -> str
    async def query_json(self, prompt: str, system_prompt: str = "", temperature: float = 0.3) -> Dict[str, Any]
```

### ReasoningStateMachine

State machine for coordinating the reasoning process.

```python
class ReasoningStateMachine:
    def __init__(self, llm: LLMInterface)
    async def transition_to_next_state(self, context: Dict[str, Any]) -> ReasoningState
    def reset(self)
```

## Methods

### reason()

Performs T1 reasoning on a problem.

```python
async def reason(
    self, 
    problem: str, 
    representation_format: str = "natural_language",
    domain: str = "general", 
    complexity_level: int = 3,
    requires_causal_analysis: bool = False
) -> ReasoningResult
```

**Parameters:**
- `problem`: The problem to solve
- `representation_format`: Format of the problem input
- `domain`: Knowledge domain of the problem
- `complexity_level`: Complexity level (1-5)
- `requires_causal_analysis`: Whether causal analysis is needed

**Returns:** `ReasoningResult` object

**Example:**
```python
result = await sdk.reason(
    problem="All birds can fly. Penguins are birds. Can penguins fly?",
    representation_format="natural_language",
    domain="logic",
    complexity_level=2
)
```

### understand()

Performs TU understanding of a proposition.

```python
async def understand(
    self, 
    proposition: str, 
    representation_format: str = "natural_language",
    domain: str = "general"
) -> UnderstandingResult
```

**Parameters:**
- `proposition`: The proposition to understand
- `representation_format`: Format of the proposition
- `domain`: Knowledge domain

**Returns:** `UnderstandingResult` object

**Example:**
```python
result = await sdk.understand(
    proposition="E = mc²",
    representation_format="formal_notation",
    domain="physics"
)
```

### deep_understand()

Performs TU* extended understanding of a proposition.

```python
async def deep_understand(
    self, 
    proposition: str, 
    representation_format: str = "natural_language",
    domain: str = "general"
) -> ExtendedUnderstandingResult
```

**Parameters:**
- `proposition`: The proposition to deeply understand
- `representation_format`: Format of the proposition
- `domain`: Knowledge domain

**Returns:** `ExtendedUnderstandingResult` object

**Example:**
```python
result = await sdk.deep_understand(
    proposition="Smoking causes lung cancer",
    representation_format="natural_language",
    domain="medicine"
)
```

### comprehensive_analysis()

Performs comprehensive analysis using all three tautologies.

```python
async def comprehensive_analysis(
    self, 
    problem: str, 
    representation_format: str = "natural_language",
    domain: str = "general"
) -> Dict[str, Any]
```

**Parameters:**
- `problem`: The problem/proposition to analyze
- `representation_format`: Format of the input
- `domain`: Knowledge domain

**Returns:** Dictionary containing results from all three tautology assessments

**Example:**
```python
result = await sdk.comprehensive_analysis(
    problem="If global warming continues, sea levels will rise",
    representation_format="natural_language",
    domain="climate_science"
)
```

## Data Structures

### ReasoningContext

```python
@dataclass
class ReasoningContext:
    problem: str
    representation_format: str
    domain: str
    complexity_level: int = 3
    uncertainty_threshold: float = 0.7
    requires_causal_analysis: bool = False
    requires_metacognition: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### ReasoningResult

```python
@dataclass
class ReasoningResult:
    solution: str
    confidence: float
    reasoning_trace: List[str]
    internal_state: Dict[str, Any]
    mode_used: ReasoningMode
    time_taken: float
    uncertainty_estimate: float
    causal_graph: Optional[Dict] = None
    state_transitions: List[str] = field(default_factory=list)
    tautology_compliance: Dict[str, bool] = field(default_factory=dict)
```

### UnderstandingResult

```python
@dataclass
class UnderstandingResult:
    internal_representation: Dict[str, Any]
    truth_value: bool
    confidence: float
    modal_invariance_score: float
    counterfactual_competence_score: float
    distribution_robustness_score: float
    understanding_trace: List[str]
    tautology_compliance: Dict[str, bool] = field(default_factory=dict)
```

### ExtendedUnderstandingResult

```python
@dataclass
class ExtendedUnderstandingResult:
    base_understanding: UnderstandingResult
    causal_structural_fidelity: Dict[str, Any]
    metacognitive_awareness: Dict[str, Any]
    phenomenal_awareness_assessment: Dict[str, Any]
    deep_understanding_score: float
    extended_trace: List[str]
    tautology_compliance: Dict[str, bool] = field(default_factory=dict)
```

## Configuration

### Representation Formats

Supported input formats:

- `natural_language`: Standard text
- `first_order_logic`: FOL expressions (∀x(P(x) → Q(x)))
- `lambda_calculus`: Lambda expressions (λx.P(x))
- `sudoku_constraints`: Sudoku puzzles
- `tower_hanoi`: Tower of Hanoi problems
- `phase_diagram`: Phase diagrams
- `iupac_string`: Chemical IUPAC notation
- `image_schema`: Visual schemas
- `braille`: Braille text
- `speech`: Speech representations
- `formal_notation`: Mathematical notation

### Knowledge Domains

Supported domains:

- `general`, `logic`, `mathematics`, `physics`, `chemistry`
- `biology`, `medicine`, `economics`, `psychology`
- `philosophy`, `computer_science`, `engineering`
- `linguistics`, `astronomy`, `geology`, `climate_science`
- `neuroscience`, `quantum_computing`, `artificial_intelligence`
- `consciousness_studies`

### Complexity Levels

- **1**: Simple, straightforward problems
- **2**: Moderate complexity
- **3**: Standard complexity (default)
- **4**: High complexity
- **5**: Very high complexity

## Error Handling

### Common Exceptions

```python
# API Key Missing
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OpenAI API key not found")

# Invalid Format
try:
    result = await sdk.reason(problem, "invalid_format")
except ValueError as e:
    print(f"Format error: {e}")

# Timeout
try:
    result = await sdk.comprehensive_analysis(complex_problem)
except asyncio.TimeoutError:
    print("Operation timed out")

# API Error
try:
    result = await sdk.reason(problem)
except openai.APIError as e:
    print(f"OpenAI API error: {e}")
```

### Error Codes

- `missing_api_key`: OpenAI API key not configured
- `invalid_format`: Unsupported representation format
- `invalid_domain`: Unknown knowledge domain
- `timeout_error`: Operation exceeded time limit
- `api_error`: OpenAI API request failed
- `parsing_error`: Input parsing failed
- `compliance_error`: Tautology compliance check failed

## Examples

### Testing Representation Invariance (T1-C1)

```python
# Same logical problem in different formats
problems = [
    ("All swans are white", "natural_language"),
    ("∀x(Swan(x) → White(x))", "first_order_logic"),
    ("λx.(Swan(x) → White(x))", "lambda_calculus")
]

for problem, format_type in problems:
    result = await sdk.reason(problem, format_type, "logic")
    print(f"Format: {format_type}, Confidence: {result.confidence}")
```

### Testing Modal Invariance (TU-C4)

```python
# Same proposition in different modalities
modalities = [
    ("Water freezes at 0°C", "natural_language"),
    ("H₂O(l) → H₂O(s) at 273.15K", "formal_notation"),
    ("[PHASE_DIAGRAM: liquid-solid at 0°C]", "phase_diagram")
]

for prop, modality in modalities:
    result = await sdk.understand(prop, modality, "physics")
    print(f"Modality: {modality}, Truth: {result.truth_value}")
```

### Testing Causal Fidelity (TU*-E1)

```python
causal_propositions = [
    "Smoking causes lung cancer",
    "Exercise improves cardiovascular health",
    "Education reduces poverty"
]

for prop in causal_propositions:
    result = await sdk.deep_understand(prop, "natural_language", "medicine")
    causal_score = result.causal_structural_fidelity.get('causal_fidelity_score', 0)
    print(f"Proposition: {prop}")
    print(f"Causal Fidelity: {causal_score:.2f}")
```

### Batch Processing

```python
async def process_batch(problems):
    sdk = AgenticReasoningSystemSDK()
    tasks = []
    
    for problem in problems:
        task = sdk.comprehensive_analysis(
            problem['text'], 
            problem['format'], 
            problem['domain']
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results

# Usage
problems = [
    {"text": "2 + 2 = 4", "format": "natural_language", "domain": "mathematics"},
    {"text": "F = ma", "format": "formal_notation", "domain": "physics"},
    {"text": "DNA stores genetic information", "format": "natural_language", "domain": "biology"}
]

results = await process_batch(problems)
```

## Advanced Usage

### Custom State Machine Configuration

```python
from config import STATE_MACHINE_CONFIG

# Modify state machine behavior
STATE_MACHINE_CONFIG['fast_processing_threshold'] = 2
STATE_MACHINE_CONFIG['verification_required'] = False

sdk = AgenticReasoningSystemSDK()
```

### Performance Optimization

```python
# Use faster model for simple problems
sdk_fast = AgenticReasoningSystemSDK(model="gpt-3.5-turbo")

# Parallel processing for multiple problems
async def parallel_reasoning(problems):
    tasks = [sdk.reason(p) for p in problems]
    return await asyncio.gather(*tasks)
```

### Custom Compliance Thresholds

```python
from config import COMPLIANCE_THRESHOLDS

# Adjust compliance requirements
COMPLIANCE_THRESHOLDS['T1']['min_confidence'] = 0.8
COMPLIANCE_THRESHOLDS['TU']['modal_invariance'] = 0.9

# Check custom compliance
result = await sdk.reason(problem)
custom_compliant = result.confidence >= 0.8
```

### Logging and Monitoring

```python
import logging

# Enable detailed logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('agentic_reasoning')

# Monitor performance
start_time = time.time()
result = await sdk.comprehensive_analysis(problem)
duration = time.time() - start_time

logger.info(f"Analysis completed in {duration:.2f}s")
logger.info(f"T1 Compliance: {result['T1_reasoning']['compliance']['T1_Overall']}")
```

### Integration with Other Systems

```python
class CustomReasoningSystem:
    def __init__(self):
        self.sdk = AgenticReasoningSystemSDK()
        self.cache = {}
    
    async def cached_reason(self, problem):
        if problem in self.cache:
            return self.cache[problem]
        
        result = await self.sdk.reason(problem)
        self.cache[problem] = result
        return result
    
    async def validate_reasoning(self, problem, expected_solution):
        result = await self.sdk.reason(problem)
        return result.solution.lower() == expected_solution.lower()
```

## Best Practices

1. **Always use async/await**: All SDK methods are asynchronous
2. **Handle exceptions**: Wrap calls in try-catch blocks
3. **Set appropriate complexity levels**: Match complexity to problem difficulty
4. **Choose correct domains**: Use specific domains for better results
5. **Monitor API usage**: Track OpenAI API costs and rate limits
6. **Validate inputs**: Check problem format and length before processing
7. **Use comprehensive analysis**: For complete tautology assessment
8. **Cache results**: Store results for repeated problems
9. **Log performance**: Monitor execution times and success rates
10. **Test compliance**: Verify tautology requirements are met

## Troubleshooting

### Common Issues

1. **API Key Error**: Ensure `OPENAI_API_KEY` environment variable is set
2. **Timeout**: Increase timeout for complex problems
3. **Low Confidence**: Try different representation formats or domains
4. **Compliance Failure**: Check if problem meets tautology requirements
5. **Format Error**: Verify representation format is supported
6. **Domain Mismatch**: Ensure domain matches problem content

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable verbose output
result = await sdk.reason(problem, complexity_level=1)
print("Reasoning trace:", result.reasoning_trace)
print("State transitions:", result.state_transitions)
```

## Support

For issues, questions, or contributions:
- Check the examples in `examples.py`
- Run tests with `python test_system.py`
- Review configuration in `config.py`
- Consult the main README.md file

## Version History

- **v1.0.0**: Initial implementation of Bhatt Conjectures framework
  - T1 Reasoning-Capability Tautology
  - TU Understanding-Capability Tautology
  - TU* Extended Understanding-Capability Tautology
  - State machine architecture
  - Comprehensive testing and examples