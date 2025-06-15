# Documentation Index

Welcome to the Agentic Reasoning System SDK documentation.

## Quick Navigation

### Getting Started
- **[Quick Start Guide](QUICK_START.md)** - Get up and running in 5 minutes
- **[Project Structure](PROJECT_STRUCTURE.md)** - Understanding the codebase organization

### Reference Documentation  
- **[API Documentation](API_DOCUMENTATION.md)** - Complete API reference
- **[JSON Parsing Fixes](JSON_PARSING_FIXES.md)** - Technical details on JSON parsing improvements

### Main Documentation
- **[Main README](../README.md)** - Project overview and comprehensive guide

## Documentation Structure

```
docs/
├── README.md                 # This index file
├── QUICK_START.md           # 5-minute getting started guide
├── API_DOCUMENTATION.md     # Complete API reference
├── JSON_PARSING_FIXES.md    # JSON parsing technical details
└── PROJECT_STRUCTURE.md     # Codebase organization guide
```

## Key Concepts

### Bhatt Conjectures Framework
The SDK implements three tautological benchmarks for AI capabilities:

1. **T1: Reasoning-Capability Tautology** - Core reasoning functionality
2. **TU: Understanding-Capability Tautology** - Understanding assessment  
3. **TU*: Extended Understanding-Capability Tautology** - Deep understanding with causal analysis

### Architecture
- **State Machine**: Coordinates reasoning processes
- **LLM Interface**: Robust OpenAI API integration
- **Ultra-Complexity Handler**: Manages high complexity problems
- **Fast/Slow Thinking**: Dynamic thinking mode coordination

## Usage Patterns

### Basic Usage
```python
from agentic_reasoning_system import AgenticReasoningSystemSDK

sdk = AgenticReasoningSystemSDK()
result = await sdk.reason("Your problem here", "natural_language", "logic")
```

### Testing
```bash
python -m pytest tests/ -v
```

### Examples
```bash
python examples/examples.py
```

## Support

For questions, issues, or contributions, please refer to the main project documentation or contact the development team.