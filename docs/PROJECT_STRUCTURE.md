# Project Structure

This document describes the organization of the Agentic Reasoning System SDK.

## Directory Structure

```
agentreasoning-sdk/
├── README.md                    # Main project documentation
├── setup.py                     # Package installation configuration
├── requirements.txt             # Python dependencies
├── pytest.ini                  # Test configuration
├── config.py                   # System configuration
├── agentic_reasoning_system.py  # Main SDK implementation
├── .gitignore                   # Git ignore rules
│
├── docs/                        # Documentation
│   ├── API_DOCUMENTATION.md     # Complete API reference
│   ├── QUICK_START.md           # Getting started guide
│   ├── JSON_PARSING_FIXES.md    # JSON parsing improvements
│   └── PROJECT_STRUCTURE.md     # This file
│
├── examples/                    # Example scripts
│   ├── __init__.py
│   ├── examples.py              # Comprehensive examples
│   └── unlimited_demo.py        # Advanced demonstrations
│
└── tests/                       # Test suite
    ├── __init__.py
    └── test_comprehensive.py    # All tests consolidated
```

## Core Components

### Main Implementation
- **`agentic_reasoning_system.py`**: Complete implementation of the Bhatt Conjectures framework
- **`config.py`**: Configuration settings for the system

### Documentation
- **`README.md`**: Main project overview and usage instructions
- **`docs/API_DOCUMENTATION.md`**: Detailed API reference
- **`docs/QUICK_START.md`**: Quick start guide for new users
- **`docs/JSON_PARSING_FIXES.md`**: Technical details on JSON parsing improvements

### Examples
- **`examples/examples.py`**: Comprehensive examples demonstrating all tautologies
- **`examples/unlimited_demo.py`**: Advanced examples showing unlimited capabilities

### Tests
- **`tests/test_comprehensive.py`**: Consolidated test suite covering all functionality
- **`pytest.ini`**: Test configuration and settings

## Key Features

### Tautology Implementations
1. **T1 Reasoning-Capability Tautology**: Core reasoning functionality
2. **TU Understanding-Capability Tautology**: Understanding assessment
3. **TU* Extended Understanding-Capability Tautology**: Deep understanding with causal analysis

### Architecture Components
- **LLMInterface**: OpenAI API integration with robust JSON parsing
- **ReasoningStateMachine**: State-based reasoning coordination
- **UltraComplexityHandler**: High complexity problem handling
- **FastSlowThinkingCoordinator**: Dynamic thinking mode coordination

## Usage Patterns

### Development Workflow
1. **Installation**: `pip install -e .` for development mode
2. **Testing**: `python -m pytest tests/ -v` for comprehensive testing
3. **Examples**: `python examples/examples.py` for demonstrations
4. **Documentation**: Reference `docs/` for detailed information

### Integration
- Import main SDK: `from agentic_reasoning_system import AgenticReasoningSystemSDK`
- Configure via `config.py` or environment variables
- Use async/await patterns for all operations

## Maintenance

### Code Organization
- Single main file for core implementation
- Separate configuration management
- Modular test structure
- Clear documentation hierarchy

### Dependencies
- **Runtime**: `openai`, `asyncio` (built-in)
- **Development**: `pytest`, `pytest-asyncio`, `pytest-cov`
- **Optional**: `black`, `flake8`, `mypy` for code quality

This structure provides clear separation of concerns while maintaining simplicity and ease of use.