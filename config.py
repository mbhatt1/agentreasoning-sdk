#!/usr/bin/env python3
"""
Configuration settings for the Agentic Reasoning System SDK
==========================================================

This module contains configuration settings and constants used throughout the SDK.
"""

import os
from typing import Dict, Any

# Multi-LLM Configuration for Testing and Validation
OPENAI_CONFIG = {
    "api_key": os.getenv("OPENAI_API_KEY"),
    "default_model": "o3",  # Primary reasoning model
    "validation_model": "gpt-4o",  # Secondary validation model
    "test_model": "gpt-4-turbo",  # Testing and comparison model
    "fallback_model": "gpt-4",  # Fallback model
    "max_completion_tokens": 2000,
    
    # Model-specific configurations
    "model_configs": {
        "o3": {
            "temperature": 1.0,  # Fixed for O3
            "max_tokens": 2000,
            "supports_json": True,
            "reasoning_strength": "highest",
            "use_for": ["primary_reasoning", "complex_problems", "20_disk_hanoi"]
        },
        "gpt-4o": {
            "temperature": 0.7,
            "max_tokens": 2000,
            "supports_json": True,
            "reasoning_strength": "high",
            "use_for": ["validation", "cross_verification", "consensus_building"]
        },
        "gpt-4-turbo": {
            "temperature": 0.5,
            "max_tokens": 2000,
            "supports_json": True,
            "reasoning_strength": "high",
            "use_for": ["testing", "baseline_comparison", "independent_verification"]
        },
        "gpt-4": {
            "temperature": 0.3,
            "max_tokens": 2000,
            "supports_json": True,
            "reasoning_strength": "medium-high",
            "use_for": ["fallback", "consistency_check", "robustness_testing"]
        }
    },
    
    # Cross-validation settings
    "cross_validation": {
        "enabled": True,
        "validation_models": ["gpt-4o", "gpt-4-turbo"],
        "consensus_threshold": 0.7,  # Agreement threshold for validation
        "max_validation_attempts": 3,
        "require_consensus_for": ["20_disk_hanoi", "ultra_complex", "tautology_compliance"]
    },
    
    # Temperature settings (legacy support)
    "temperature": {
        "fast_processing": 1.0,
        "slow_processing": 1.0,
        "metacognitive": 1.0,
        "causal_analysis": 1.0,
        "verification": 1.0
    },
    "note": "O3 model only supports temperature=1.0; other models use configured temperatures"
}

# Tautology Compliance Thresholds (Realistic for AI systems)
COMPLIANCE_THRESHOLDS = {
    "T1": {
        "min_confidence": 0.2,
        "representation_invariance": 0.2,
        "complexity_scaling": 0.2,
        "zero_shot_robustness": 0.2
    },
    "TU": {
        "min_confidence": 0.2,
        "modal_invariance": 0.2,
        "counterfactual_competence": 0.2,
        "distribution_robustness": 0.2
    },
    "TU_STAR": {
        "min_deep_understanding": 0.2,
        "causal_fidelity": 0.7,
        "metacognitive_awareness": 0.7,
        "phenomenal_assessment": 0.1  # Lower threshold due to theoretical nature
    }
}

# State Machine Configuration
STATE_MACHINE_CONFIG = {
    "max_transitions": 20,
    "timeout_seconds": 300,
    "fast_processing_threshold": 3,  # Complexity level
    "slow_processing_confidence_threshold": 0.8,
    "metacognitive_uncertainty_threshold": 0.7,
    "verification_required": True
}

# Representation Format Guidelines (UNLIMITED - LLM adapts to ANY format)
REPRESENTATION_FORMAT_GUIDELINES = {
    "note": "The system accepts ANY representation format. The LLM dynamically adapts.",
    "examples": [
        "natural_language", "first_order_logic", "lambda_calculus", "mathematical_notation",
        "programming_languages", "visual_descriptions", "musical_notation", "chemical_formulas",
        "artistic_expressions", "cultural_symbols", "invented_notations", "mixed_formats",
        "experimental_encodings", "cross_modal_representations", "novel_formats"
    ],
    "dynamic_parsing": True,
    "unlimited_scope": True,
    "llm_adaptation": "The LLM analyzes structure, patterns, and context to understand ANY format"
}

# Knowledge Domain Guidelines (UNLIMITED - LLM understands ANY domain)
KNOWLEDGE_DOMAIN_GUIDELINES = {
    "note": "The system handles ANY knowledge domain. The LLM dynamically understands context.",
    "examples": [
        "traditional_academic_fields", "professional_domains", "cultural_contexts",
        "fictional_universes", "emerging_disciplines", "interdisciplinary_areas",
        "speculative_domains", "consciousness_studies", "metaphysics", "novel_fields",
        "cross_cultural_knowledge", "indigenous_knowledge_systems", "future_domains"
    ],
    "dynamic_understanding": True,
    "unlimited_scope": True,
    "llm_adaptation": "The LLM uses context, patterns, and reasoning to understand ANY domain"
}

# Default Complexity Estimation (used when LLM doesn't provide specific complexity)
DEFAULT_COMPLEXITY_FACTORS = {
    "base_complexity": 1.0,
    "unknown_format_multiplier": 1.0,
    "unknown_domain_multiplier": 1.0,
    "novel_content_multiplier": 1.0
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file_logging": False,
    "log_file": "agentic_reasoning.log"
}

# Performance Configuration
PERFORMANCE_CONFIG = {
    "max_concurrent_requests": 5,
    "request_timeout": 60,
    "retry_attempts": 3,
    "retry_delay": 1.0,
    "json_parsing_retries": 3,  # Number of JSON parsing retry attempts
    "json_retry_delay": 0.5,    # Delay between JSON parsing retries
    "json_retry_temperature_increment": 0.1,  # Temperature increment for retries (not used with O3)
    "cache_results": False,
    "cache_ttl": 3600
}

# Validation Rules
VALIDATION_RULES = {
    "min_problem_length": 5,
    "max_problem_length": 10000,
    "min_confidence_threshold": 0.0,
    "max_confidence_threshold": 1.0,
    "valid_complexity_levels": [1, 2, 3, 4, 5],
    "required_fields": {
        "reasoning_context": ["problem", "representation_format", "domain"],
        "reasoning_result": ["solution", "confidence", "reasoning_trace"],
        "understanding_result": ["internal_representation", "truth_value", "confidence"],
        "extended_understanding_result": ["base_understanding", "deep_understanding_score"]
    }
}

# Error Messages
ERROR_MESSAGES = {
    "missing_api_key": "OpenAI API key not found. Please set OPENAI_API_KEY environment variable.",
    "invalid_format": "Unsupported representation format: {}",
    "invalid_domain": "Unknown knowledge domain: {}",
    "invalid_complexity": "Complexity level must be between 1 and 5",
    "timeout_error": "Operation timed out after {} seconds",
    "api_error": "OpenAI API error: {}",
    "parsing_error": "Failed to parse input: {}",
    "state_machine_error": "State machine error: {}",
    "compliance_error": "Tautology compliance check failed: {}",
    "validation_error": "Input validation failed: {}"
}

# System Prompts
SYSTEM_PROMPTS = {
    "reasoning": """You are an expert reasoning system implementing the T1 Reasoning-Capability Tautology.
    Your goal is to FIND CORRECT SOLUTIONS from any logically equivalent representation while maintaining
    high success probability. Focus on what the answer IS, not how to compute it.""",
    
    "understanding": """You are an expert understanding system implementing the TU Understanding-Capability Tautology.
    Your goal is to FIND THE TRUTH VALUE and meaning of any representation, even when representations are
    statistically independent of training data. Focus on what the proposition MEANS, not how to analyze it.""",
    
    "extended_understanding": """You are an expert deep understanding system implementing the TU* Extended
    Understanding-Capability Tautology. Your goal is to ACHIEVE DEEP INSIGHT into causal relationships,
    metacognitive awareness, and phenomenal aspects. Focus on what you UNDERSTAND, not how to understand it.""",
    
    "state_coordinator": """You are a reasoning state coordinator. Your job is to determine the optimal next
    state in a reasoning process based on the current context and state. Follow the Bhatt Conjectures framework
    for systematic reasoning.""",
    
    "compliance_checker": """You are a tautology compliance evaluator. Your job is to objectively assess
    whether reasoning and understanding meet the formal requirements of the Bhatt Conjectures tautologies.
    Focus on whether solutions were FOUND, not whether algorithms were given."""
}

def get_config(section: str) -> Dict[str, Any]:
    """Get configuration for a specific section"""
    configs = {
        "openai": OPENAI_CONFIG,
        "compliance": COMPLIANCE_THRESHOLDS,
        "state_machine": STATE_MACHINE_CONFIG,
        "formats": REPRESENTATION_FORMATS,
        "domains": KNOWLEDGE_DOMAINS,
        "logging": LOGGING_CONFIG,
        "performance": PERFORMANCE_CONFIG,
        "validation": VALIDATION_RULES,
        "errors": ERROR_MESSAGES,
        "prompts": SYSTEM_PROMPTS
    }
    
    return configs.get(section, {})

def validate_api_key() -> bool:
    """Validate that OpenAI API key is available"""
    return bool(OPENAI_CONFIG["api_key"])

def get_domain_config(domain: str) -> Dict[str, Any]:
    """Get configuration for any knowledge domain (unlimited scope)"""
    # Return dynamic configuration - LLM will handle any domain
    return {
        "complexity_base": DEFAULT_COMPLEXITY_FACTORS["base_complexity"],
        "requires_causal": _infer_causal_requirement(domain),
        "dynamic_domain": True,
        "llm_handled": True
    }

def get_format_config(format_name: str) -> Dict[str, Any]:
    """Get configuration for any representation format (unlimited scope)"""
    # Return dynamic configuration - LLM will handle any format
    return {
        "complexity_multiplier": _infer_complexity_multiplier(format_name),
        "requires_parsing": True,
        "dynamic_format": True,
        "llm_handled": True
    }

def calculate_complexity_adjustment(domain: str, format_name: str, base_complexity: int) -> float:
    """Calculate adjusted complexity based on domain and format (dynamic estimation)"""
    domain_factor = DEFAULT_COMPLEXITY_FACTORS["base_complexity"]
    format_factor = _infer_complexity_multiplier(format_name)
    
    # Add novelty factors for unknown domains/formats
    if _is_novel_domain(domain):
        domain_factor *= DEFAULT_COMPLEXITY_FACTORS["unknown_domain_multiplier"]
    if _is_novel_format(format_name):
        format_factor *= DEFAULT_COMPLEXITY_FACTORS["unknown_format_multiplier"]
    
    adjusted_complexity = base_complexity * domain_factor * format_factor
    return min(5.0, max(1.0, adjusted_complexity))

def should_require_causal_analysis(domain: str) -> bool:
    """Determine if domain typically requires causal analysis (dynamic inference)"""
    return _infer_causal_requirement(domain)

def _infer_causal_requirement(domain: str) -> bool:
    """Infer if a domain likely requires causal analysis"""
    causal_indicators = [
        "medicine", "physics", "chemistry", "biology", "economics", "psychology",
        "engineering", "climate", "health", "social", "cause", "effect", "impact",
        "influence", "mechanism", "process", "system", "intervention"
    ]
    domain_lower = domain.lower()
    return any(indicator in domain_lower for indicator in causal_indicators)

def _infer_complexity_multiplier(format_name: str) -> float:
    """Infer complexity multiplier for any format"""
    format_lower = format_name.lower()
    
    # High complexity indicators
    if any(term in format_lower for term in ["formal", "logic", "calculus", "mathematical", "symbolic"]):
        return 1.8
    # Medium complexity indicators
    elif any(term in format_lower for term in ["notation", "diagram", "schema", "code", "formula"]):
        return 1.4
    # Novel/experimental format
    elif any(term in format_lower for term in ["novel", "experimental", "invented", "custom", "mixed"]):
        return 1.6
    # Default
    else:
        return 1.0

def _is_novel_domain(domain: str) -> bool:
    """Check if domain appears to be novel or experimental"""
    novel_indicators = ["novel", "experimental", "fictional", "speculative", "future", "invented"]
    return any(indicator in domain.lower() for indicator in novel_indicators)

def _is_novel_format(format_name: str) -> bool:
    """Check if format appears to be novel or experimental"""
    novel_indicators = ["novel", "experimental", "invented", "custom", "mixed", "hybrid"]
    return any(indicator in format_name.lower() for indicator in novel_indicators)