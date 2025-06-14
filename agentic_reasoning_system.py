#!/usr/bin/env python3
"""
Agentic Reasoning System SDK - Implementation of Bhatt Conjectures
================================================================

This system implements the three tautologies from the Bhatt Conjectures paper:
- T1: Reasoning-Capability Tautology
- TU: Understanding-Capability Tautology  
- TU*: Extended Understanding-Capability Tautology

The system uses OpenAI's LLM for all reasoning, parsing, and understanding tasks.
State machine architecture coordinates different reasoning modes.
"""

import json
import time
import asyncio
from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, Union
import logging
import openai
import os
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ReasoningMode(Enum):
    """Different modes of reasoning based on Fast/Slow thinking"""
    FAST_INTUITIVE = "fast_intuitive"
    SLOW_DELIBERATIVE = "slow_deliberative"
    METACOGNITIVE = "metacognitive"
    CAUSAL = "causal"

class ReasoningState(Enum):
    """States in the reasoning state machine"""
    IDLE = "idle"
    PARSING_INPUT = "parsing_input"
    REPRESENTATION_MAPPING = "representation_mapping"
    FAST_PROCESSING = "fast_processing"
    SLOW_PROCESSING = "slow_processing"
    METACOGNITIVE_EVALUATION = "metacognitive_evaluation"
    CAUSAL_ANALYSIS = "causal_analysis"
    GENERATING_RESPONSE = "generating_response"
    SELF_VERIFICATION = "self_verification"
    COMPLETE = "complete"
    ERROR = "error"

@dataclass
class ReasoningContext:
    """Context for reasoning operations"""
    problem: str
    representation_format: str
    domain: str
    complexity_level: int = 3
    uncertainty_threshold: float = 0.7
    requires_causal_analysis: bool = False
    requires_metacognition: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ReasoningResult:
    """Result of reasoning operation"""
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

@dataclass
class UnderstandingResult:
    """Result of understanding operation"""
    internal_representation: Dict[str, Any]
    truth_value: bool
    confidence: float
    modal_invariance_score: float
    counterfactual_competence_score: float
    distribution_robustness_score: float
    understanding_trace: List[str]
    tautology_compliance: Dict[str, bool] = field(default_factory=dict)

@dataclass
class ExtendedUnderstandingResult:
    """Result of extended understanding operation (TU*)"""
    base_understanding: UnderstandingResult
    causal_structural_fidelity: Dict[str, Any]
    metacognitive_awareness: Dict[str, Any]
    phenomenal_awareness_assessment: Dict[str, Any]
    deep_understanding_score: float
    extended_trace: List[str]
    tautology_compliance: Dict[str, bool] = field(default_factory=dict)

class LLMInterface:
    """Interface to OpenAI's LLM for all reasoning tasks"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4.1-nano"):
        self.client = openai.OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model
        
    async def query(self, prompt: str, system_prompt: str = "", temperature: float = 1.0,
                   max_completion_tokens: int = 2000) -> str:
        """Query the LLM with given prompt"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_completion_tokens=max_completion_tokens
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM query failed: {str(e)}")
            raise
    
    async def query_json(self, prompt: str, system_prompt: str = "", temperature: float = 1.0) -> Dict[str, Any]:
        """Query LLM and expect JSON response with robust parsing"""
        json_prompt = f"{prompt}\n\nIMPORTANT: Respond with valid JSON only. Start with {{ and end with }}. No additional text."
        response = await self.query(json_prompt, system_prompt, temperature)
        
        # Multiple parsing strategies for o3 model compatibility
        parsing_strategies = [
            # Strategy 1: Extract first complete JSON object
            lambda r: self._extract_json_object(r),
            # Strategy 2: Clean and parse entire response
            lambda r: json.loads(self._clean_json_response(r)),
            # Strategy 3: Try parsing response as-is
            lambda r: json.loads(r.strip()),
            # Strategy 4: Extract content between code blocks
            lambda r: self._extract_from_code_blocks(r),
        ]
        
        for i, strategy in enumerate(parsing_strategies):
            try:
                result = strategy(response)
                if isinstance(result, dict):
                    return result
            except (json.JSONDecodeError, ValueError, AttributeError) as e:
                logger.debug(f"JSON parsing strategy {i+1} failed: {str(e)}")
                continue
        
        # Final fallback: return a structured error response
        logger.error(f"All JSON parsing strategies failed for response: {response[:200]}...")
        return self._create_fallback_response(response)
    
    def _extract_json_object(self, response: str) -> Dict[str, Any]:
        """Extract the first complete JSON object from response"""
        start_idx = response.find('{')
        if start_idx == -1:
            raise ValueError("No JSON object found")
        
        brace_count = 0
        for i, char in enumerate(response[start_idx:], start_idx):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    json_str = response[start_idx:i+1]
                    return json.loads(json_str)
        
        raise ValueError("Incomplete JSON object")
    
    def _clean_json_response(self, response: str) -> str:
        """Clean response for JSON parsing"""
        # Remove common non-JSON prefixes/suffixes
        response = response.strip()
        
        # Remove markdown code blocks
        if response.startswith('```'):
            lines = response.split('\n')
            if len(lines) > 2:
                response = '\n'.join(lines[1:-1])
        
        # Remove common prefixes
        prefixes_to_remove = [
            "Here's the JSON response:",
            "JSON response:",
            "Response:",
            "```json",
            "```"
        ]
        
        for prefix in prefixes_to_remove:
            if response.startswith(prefix):
                response = response[len(prefix):].strip()
        
        return response
    
    def _extract_from_code_blocks(self, response: str) -> Dict[str, Any]:
        """Extract JSON from markdown code blocks"""
        import re
        
        # Look for JSON in code blocks
        code_block_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        match = re.search(code_block_pattern, response, re.DOTALL)
        
        if match:
            return json.loads(match.group(1))
        
        raise ValueError("No JSON found in code blocks")
    
    def _create_fallback_response(self, original_response: str) -> Dict[str, Any]:
        """Create a fallback response when JSON parsing fails"""
        return {
            "error": "json_parsing_failed",
            "original_response": original_response[:500],  # Truncate for safety
            "confidence": 0.1,
            "solution": "JSON parsing failed - using fallback response",
            "reasoning_steps": ["Failed to parse LLM response as JSON"],
            "compliance_score": 0.0,
            "r1_compliance": False,
            "r2_compliance": False,
            "c1_compliance": False,
            "c2_compliance": False,
            "c3_compliance": False,
            "overall_t1_compliance": False,
            "u1_compliance": False,
            "u2_compliance": False,
            "c4_compliance": False,
            "c5_compliance": False,
            "c6_compliance": False,
            "overall_tu_compliance": False,
            "e1_compliance": False,
            "e2_compliance": False,
            "e3_compliance": False,
            "overall_tustar_compliance": False,
            "verification_passed": False,
            "verification_score": 0.0,
            "should_revise": True
        }

class ReasoningStateMachine:
    """State machine for coordinating reasoning process"""
    
    def __init__(self, llm: LLMInterface):
        self.llm = llm
        self.current_state = ReasoningState.IDLE
        self.state_history: List[ReasoningState] = []
        self.context: Dict[str, Any] = {}
        
    async def transition_to_next_state(self, context: Dict[str, Any]) -> ReasoningState:
        """Determine next state based on current context"""
        
        transition_prompt = f"""
        Current reasoning state: {self.current_state}
        Context: {json.dumps(context, indent=2)}
        
        Based on the current state and context, determine the next appropriate state for reasoning.
        Consider:
        - Complexity level: {context.get('complexity_level', 3)}
        - Confidence level: {context.get('confidence', 0.5)}
        - Requires causal analysis: {context.get('requires_causal_analysis', False)}
        - Requires metacognition: {context.get('requires_metacognition', True)}
        - Current processing results: {context.get('processing_complete', False)}
        
        Available states: {[state.value for state in ReasoningState]}
        
        Return the next state as a JSON object: {{"next_state": "state_name", "reason": "explanation"}}
        """
        
        system_prompt = """You are a reasoning state coordinator. Your job is to determine the optimal next state 
        in a reasoning process based on the current context and state. Follow the Bhatt Conjectures framework 
        for systematic reasoning."""
        
        try:
            response = await self.llm.query_json(transition_prompt, system_prompt)
            next_state_name = response.get('next_state', 'error')
            
            # Convert string to enum
            for state in ReasoningState:
                if state.value == next_state_name:
                    self.state_history.append(self.current_state)
                    self.current_state = state
                    logger.info(f"State transition: {self.state_history[-1]} -> {self.current_state}")
                    return state
            
            # Fallback to error state
            self.current_state = ReasoningState.ERROR
            return ReasoningState.ERROR
            
        except Exception as e:
            logger.error(f"State transition failed: {str(e)}")
            self.current_state = ReasoningState.ERROR
            return ReasoningState.ERROR
    
    def reset(self):
        """Reset state machine"""
        self.current_state = ReasoningState.IDLE
        self.state_history.clear()
        self.context.clear()

class T1ReasoningEngine:
    """T1: Reasoning-Capability Tautology Implementation"""
    
    def __init__(self, llm: LLMInterface):
        self.llm = llm
        self.state_machine = ReasoningStateMachine(llm)
    
    def _safe_float(self, value, default=0.0):
        """Safely convert value to float"""
        try:
            return float(value) if value is not None else default
        except (ValueError, TypeError):
            return default
    
    async def reason(self, context: ReasoningContext) -> ReasoningResult:
        """Main reasoning method implementing T1 tautology"""
        start_time = time.time()
        reasoning_trace = []
        state_transitions = []
        
        # Reset state machine
        self.state_machine.reset()
        
        # Initialize context
        sm_context = {
            'problem': context.problem,
            'representation_format': context.representation_format,
            'domain': context.domain,
            'complexity_level': context.complexity_level,
            'requires_causal_analysis': context.requires_causal_analysis,
            'requires_metacognition': context.requires_metacognition,
            'uncertainty_threshold': context.uncertainty_threshold
        }
        
        # Process through state machine
        while self.state_machine.current_state not in [ReasoningState.COMPLETE, ReasoningState.ERROR]:
            current_state = self.state_machine.current_state
            state_transitions.append(current_state.value)
            
            if current_state == ReasoningState.IDLE:
                sm_context['ready_to_parse'] = True
                
            elif current_state == ReasoningState.PARSING_INPUT:
                result = await self._parse_input(context, reasoning_trace)
                sm_context.update(result)
                
            elif current_state == ReasoningState.REPRESENTATION_MAPPING:
                result = await self._map_representation(sm_context, reasoning_trace)
                sm_context.update(result)
                
            elif current_state == ReasoningState.FAST_PROCESSING:
                result = await self._fast_processing(sm_context, reasoning_trace)
                sm_context.update(result)
                
            elif current_state == ReasoningState.SLOW_PROCESSING:
                result = await self._slow_processing(sm_context, reasoning_trace)
                sm_context.update(result)
                
            elif current_state == ReasoningState.METACOGNITIVE_EVALUATION:
                result = await self._metacognitive_evaluation(sm_context, reasoning_trace)
                sm_context.update(result)
                
            elif current_state == ReasoningState.CAUSAL_ANALYSIS:
                result = await self._causal_analysis(sm_context, reasoning_trace)
                sm_context.update(result)
                
            elif current_state == ReasoningState.GENERATING_RESPONSE:
                result = await self._generate_response(sm_context, reasoning_trace)
                sm_context.update(result)
                
            elif current_state == ReasoningState.SELF_VERIFICATION:
                result = await self._self_verification(sm_context, reasoning_trace)
                sm_context.update(result)
            
            # Transition to next state
            await self.state_machine.transition_to_next_state(sm_context)
        
        # Check T1 compliance
        t1_compliance = await self._check_t1_compliance(sm_context, context)
        
        end_time = time.time()
        
        return ReasoningResult(
            solution=sm_context.get('final_solution', 'No solution generated'),
            confidence=sm_context.get('confidence', 0.0),
            reasoning_trace=reasoning_trace,
            internal_state=sm_context.get('internal_representation', {}),
            mode_used=ReasoningMode.SLOW_DELIBERATIVE,
            time_taken=end_time - start_time,
            uncertainty_estimate=1.0 - self._safe_float(sm_context.get('confidence', 0.0)),
            causal_graph=sm_context.get('causal_graph'),
            state_transitions=state_transitions,
            tautology_compliance=t1_compliance
        )
    
    async def _parse_input(self, context: ReasoningContext, trace: List[str]) -> Dict[str, Any]:
        """Parse input using LLM - handles any representation format"""
        
        parse_prompt = f"""
        Parse and analyze the following problem in {context.representation_format} format:
        
        Problem: {context.problem}
        Domain: {context.domain}
        
        Extract:
        1. Core logical structure
        2. Key entities and relationships
        3. Constraints and conditions
        4. Problem type and complexity
        5. Required reasoning approach
        
        Provide analysis as JSON with fields: logical_structure, entities, relationships, 
        constraints, problem_type, complexity_level, reasoning_approach.
        """
        
        system_prompt = """You are an expert at parsing problems in any representation format 
        (natural language, formal logic, lambda calculus, diagrams, etc.). Extract the essential 
        logical structure regardless of surface representation."""
        
        try:
            response = await self.llm.query_json(parse_prompt, system_prompt)
            trace.append(f"Parsed {context.representation_format} input successfully")
            
            return {
                'parsed_input': response,
                'parsing_complete': True,
                'complexity_level': response.get('complexity_level', 3)
            }
        except Exception as e:
            trace.append(f"Parsing failed: {str(e)}")
            return {'parsing_error': True, 'error_message': str(e)}
    
    async def _map_representation(self, context: Dict[str, Any], trace: List[str]) -> Dict[str, Any]:
        """Map parsed input to internal representation"""
        
        mapping_prompt = f"""
        Create an internal representation from the parsed input that preserves logical structure
        across different surface representations.
        
        Parsed Input: {json.dumps(context.get('parsed_input', {}), indent=2)}
        
        Create a representation that:
        1. Preserves truth conditions
        2. Enables logical inference
        3. Supports counterfactual reasoning
        4. Is format-independent
        
        Return as JSON with fields: truth_conditions, inference_rules, entities, relations, 
        logical_form, semantic_features.
        """
        
        system_prompt = """You create internal representations that capture the essential logical 
        structure of problems, independent of their surface format. Focus on truth-preserving mappings."""
        
        try:
            response = await self.llm.query_json(mapping_prompt, system_prompt)
            trace.append("Created internal representation")
            
            return {
                'internal_representation': response,
                'representation_complete': True
            }
        except Exception as e:
            trace.append(f"Representation mapping failed: {str(e)}")
            return {'mapping_error': True}
    
    async def _fast_processing(self, context: Dict[str, Any], trace: List[str]) -> Dict[str, Any]:
        """Fast, intuitive processing mode"""
        
        fast_prompt = f"""
        Perform fast, intuitive reasoning using SPECIFIC PATTERN RECOGNITION CRITERIA:
        
        Internal Representation: {json.dumps(context.get('internal_representation', {}), indent=2)}
        Problem: {context.get('problem', '')}
        
        FAST REASONING STRATEGY:
        1. IMMEDIATE PATTERN RECOGNITION:
        - Identify problem type (logical, mathematical, causal, etc.)
        - Match to known solution patterns
        - Apply standard heuristics for this problem type
        
        2. FAMILIAR PROBLEM MAPPING:
        - Compare to similar problems you've seen
        - Use analogical reasoning
        - Apply template solutions
        
        3. QUICK HEURISTIC APPLICATION:
        - Use domain-specific shortcuts
        - Apply rules of thumb
        - Generate rapid approximations
        
        CONFIDENCE CALIBRATION:
        - High confidence (0.8-1.0): Clear pattern match, standard problem type, confident in heuristic
        - Medium confidence (0.5-0.7): Partial pattern match, some uncertainty in approach
        - Low confidence (0.0-0.4): Unclear pattern, novel problem type, heuristics may not apply
        
        QUALITY REQUIREMENTS:
        - Solution must address the core problem
        - Reasoning steps must be logical (even if fast)
        - Patterns used must be relevant to the problem type
        - Confidence must reflect actual certainty level
        
        Return JSON with: solution, confidence (0-1), reasoning_steps, patterns_used.
        """
        
        system_prompt = """You are in fast thinking mode. Use intuition, pattern recognition, 
        and heuristics to quickly solve problems. Don't overthink - go with your first instinct."""
        
        try:
            response = await self.llm.query_json(fast_prompt, system_prompt, temperature=1.0)
            trace.append("Completed fast processing")
            
            confidence = response.get('confidence', 0.5)
            
            return {
                'fast_solution': response.get('solution', ''),
                'confidence': confidence,
                'fast_reasoning': response.get('reasoning_steps', []),
                'patterns_used': response.get('patterns_used', []),
                'fast_processing_complete': True,
                'needs_slow_processing': confidence < 0.8
            }
        except Exception as e:
            trace.append(f"Fast processing failed: {str(e)}")
            return {'fast_processing_error': True}
    
    async def _slow_processing(self, context: Dict[str, Any], trace: List[str]) -> Dict[str, Any]:
        """Slow, deliberative processing mode"""
        
        slow_prompt = f"""
        Perform careful, deliberative reasoning using SYSTEMATIC LOGICAL ANALYSIS:
        
        Internal Representation: {json.dumps(context.get('internal_representation', {}), indent=2)}
        Problem: {context.get('problem', '')}
        Fast Solution (if any): {context.get('fast_solution', 'None')}
        
        SYSTEMATIC REASONING PROTOCOL:
        
        1. PROBLEM DECOMPOSITION:
        - Break problem into logical components
        - Identify key variables and relationships
        - Determine what needs to be proven/solved
        - List all given information and constraints
        
        2. FORMAL LOGICAL ANALYSIS:
        - Apply appropriate logical rules (modus ponens, universal instantiation, etc.)
        - Use valid inference patterns
        - Maintain logical rigor throughout
        - Document each logical step
        
        3. MULTIPLE SOLUTION PATHS:
        - Consider at least 2-3 different approaches
        - Compare approaches for validity
        - Choose the most rigorous method
        - Document why other approaches were rejected
        
        4. STEP-BY-STEP VERIFICATION:
        - Verify each logical step independently
        - Check for hidden assumptions
        - Ensure conclusions follow from premises
        - Test edge cases and boundary conditions
        
        5. LOGICAL CONSISTENCY CHECK:
        - Ensure no contradictions in reasoning
        - Verify solution satisfies all constraints
        - Check compatibility with domain knowledge
        - Validate final answer against original problem
        
        CONFIDENCE CALIBRATION:
        - High confidence (0.8-1.0): Rigorous logical proof, multiple verification checks passed
        - Medium confidence (0.6-0.7): Sound reasoning but some uncertainty in steps
        - Low confidence (0.0-0.5): Logical gaps, unverified assumptions, or incomplete analysis
        
        QUALITY REQUIREMENTS:
        - Each step must be logically justified
        - All logical rules used must be explicitly stated
        - Verification checks must be specific and testable
        - Alternative approaches must be genuinely different methods
        
        Return JSON with: solution, confidence (0-1), detailed_steps, logical_rules_used,
        verification_checks, alternative_approaches.
        """
        
        system_prompt = """You are in slow thinking mode. Use careful, systematic reasoning. 
        Apply formal logic, check your work, consider alternatives. Be thorough and precise."""
        
        try:
            response = await self.llm.query_json(slow_prompt, system_prompt, temperature=1.0)
            trace.append("Completed slow processing")
            
            return {
                'slow_solution': response.get('solution', ''),
                'confidence': response.get('confidence', 0.7),
                'detailed_reasoning': response.get('detailed_steps', []),
                'logical_rules': response.get('logical_rules_used', []),
                'verification_checks': response.get('verification_checks', []),
                'slow_processing_complete': True
            }
        except Exception as e:
            trace.append(f"Slow processing failed: {str(e)}")
            return {'slow_processing_error': True}
    
    async def _metacognitive_evaluation(self, context: Dict[str, Any], trace: List[str]) -> Dict[str, Any]:
        """Metacognitive evaluation of reasoning process"""
        
        meta_prompt = f"""
        Perform SYSTEMATIC METACOGNITIVE EVALUATION using SPECIFIC CRITERIA:
        
        Problem: {context.get('problem', '')}
        Current Solution: {context.get('slow_solution') or context.get('fast_solution', '')}
        Reasoning Steps: {context.get('detailed_reasoning', [])}
        
        METACOGNITIVE ANALYSIS PROTOCOL:
        
        1. CONFIDENCE ASSESSMENT:
        - High (0.8-1.0): Strong logical foundation, multiple verification checks passed, high certainty
        - Medium (0.5-0.7): Sound reasoning but some gaps or uncertainties
        - Low (0.0-0.4): Significant gaps, weak reasoning, or high uncertainty
        - Base confidence on: logical rigor, evidence quality, verification results
        
        2. ERROR IDENTIFICATION:
        - Logical errors: Invalid inferences, fallacies, contradiction
        - Factual errors: Incorrect domain knowledge, false premises
        - Procedural errors: Wrong method application, calculation mistakes
        - Completeness errors: Missing steps, incomplete analysis
        
        3. REASONING QUALITY EVALUATION (0-1 scale):
        - Structure (0.25): Clear logical flow, organized steps
        - Validity (0.25): Sound logical rules, valid inferences
        - Completeness (0.25): All necessary steps included
        - Rigor (0.25): Thorough analysis, proper verification
        
        4. ALTERNATIVE INTERPRETATIONS:
        - Consider different problem interpretations
        - Evaluate alternative solution approaches
        - Assess if current interpretation is most reasonable
        
        5. UNCERTAINTY AND LIMITATIONS:
        - Knowledge gaps: Areas where information is incomplete
        - Methodological limitations: Constraints of chosen approach
        - Assumption dependencies: Critical assumptions that may be wrong
        - Scope limitations: What the solution doesn't address
        
        6. IMPROVEMENT SUGGESTIONS:
        - Specific steps to strengthen reasoning
        - Additional verification needed
        - Alternative approaches to consider
        - Areas requiring more analysis
        
        REVISION DECISION CRITERIA:
        - should_revise = True if: Major errors found, confidence < 0.6, significant gaps identified
        - should_revise = False if: Minor issues only, confidence ≥ 0.6, reasoning is sound
        
        Return JSON with: confidence_assessment, potential_errors, reasoning_quality_score (0-1),
        uncertainty_sources, limitations, suggested_improvements, should_revise.
        """
        
        system_prompt = """You are evaluating your own reasoning. Be honest about limitations, 
        uncertainties, and potential errors. Assess the quality of your reasoning process."""
        
        try:
            response = await self.llm.query_json(meta_prompt, system_prompt, temperature=1.0)
            trace.append("Completed metacognitive evaluation")
            
            return {
                'metacognitive_assessment': response,
                'confidence': response.get('confidence_assessment', 0.7),
                'should_revise': response.get('should_revise', False),
                'metacognitive_complete': True
            }
        except Exception as e:
            trace.append(f"Metacognitive evaluation failed: {str(e)}")
            return {'metacognitive_error': True}
    
    async def _causal_analysis(self, context: Dict[str, Any], trace: List[str]) -> Dict[str, Any]:
        """Causal analysis for problems requiring causal reasoning"""
        
        causal_prompt = f"""
        Perform causal analysis of the problem:
        
        Problem: {context.get('problem', '')}
        Internal Representation: {json.dumps(context.get('internal_representation', {}), indent=2)}
        
        Analyze causal structure:
        1. Identify causal variables
        2. Determine causal relationships
        3. Build causal graph
        4. Consider interventions (do-calculus)
        5. Analyze counterfactuals
        
        Return JSON with: causal_variables, causal_relationships, causal_graph, 
        possible_interventions, counterfactual_scenarios.
        """
        
        system_prompt = """You are performing causal analysis. Focus on identifying true causal 
        relationships, not just correlations. Consider what would happen under interventions."""
        
        try:
            response = await self.llm.query_json(causal_prompt, system_prompt)
            trace.append("Completed causal analysis")
            
            return {
                'causal_analysis': response,
                'causal_graph': response.get('causal_graph', {}),
                'causal_analysis_complete': True
            }
        except Exception as e:
            trace.append(f"Causal analysis failed: {str(e)}")
            return {'causal_analysis_error': True}
    
    async def _generate_response(self, context: Dict[str, Any], trace: List[str]) -> Dict[str, Any]:
        """Generate final response"""
        
        response_prompt = f"""
        Generate the final solution based on all reasoning performed:
        
        Problem: {context.get('problem', '')}
        Fast Solution: {context.get('fast_solution', '')}
        Slow Solution: {context.get('slow_solution', '')}
        Metacognitive Assessment: {context.get('metacognitive_assessment', {})}
        Causal Analysis: {context.get('causal_analysis', {})}
        
        Synthesize the best solution considering all analyses.
        
        Return JSON with: final_solution, confidence (0-1), synthesis_reasoning, 
        key_insights, solution_quality.
        """
        
        system_prompt = """Synthesize all reasoning to produce the best possible solution. 
        Consider all analyses performed and provide a well-reasoned final answer."""
        
        try:
            response = await self.llm.query_json(response_prompt, system_prompt)
            trace.append("Generated final response")
            
            return {
                'final_solution': response.get('final_solution', ''),
                'confidence': response.get('confidence', 0.7),
                'synthesis_reasoning': response.get('synthesis_reasoning', []),
                'response_complete': True
            }
        except Exception as e:
            trace.append(f"Response generation failed: {str(e)}")
            return {'response_error': True}
    
    async def _self_verification(self, context: Dict[str, Any], trace: List[str]) -> Dict[str, Any]:
        """Self-verification of solution"""
        
        verify_prompt = f"""
        Verify the final solution using SPECIFIC VERIFICATION CRITERIA:
        
        Problem: {context.get('problem', '')}
        Final Solution: {context.get('final_solution', '')}
        
        VERIFICATION CHECKLIST (Each must PASS for overall verification):
        
        1. PROBLEM ADDRESSING:
        - PASS if: Solution directly answers the original problem, addresses all parts of the question
        - FAIL if: Solution is off-topic, misses key aspects, or answers a different question
        
        2. LOGICAL SOUNDNESS:
        - PASS if: Reasoning follows valid logical rules, conclusions follow from premises, no logical fallacies
        - FAIL if: Contains logical errors, invalid inferences, or fallacious reasoning
        
        3. CONTRADICTION CHECK:
        - PASS if: No internal contradictions, consistent throughout, coherent reasoning chain
        - FAIL if: Contains contradictory statements, inconsistent claims, or conflicting conclusions
        
        4. CONSTRAINT SATISFACTION:
        - PASS if: Meets all stated constraints, follows problem requirements, respects boundaries
        - FAIL if: Violates constraints, ignores requirements, or exceeds specified limits
        
        5. DOMAIN KNOWLEDGE CONSISTENCY:
        - PASS if: Consistent with established domain knowledge, uses correct domain concepts
        - FAIL if: Contradicts established facts, misuses domain concepts, or shows domain ignorance
        
        SCORING INSTRUCTIONS:
        - verification_passed = True ONLY if ALL 5 checks PASS
        - verification_score = (number of passed checks) / 5
        - List specific issues found for any failed checks
        - Adjust confidence down if verification issues found
        
        Return JSON with: verification_passed (boolean), verification_score (0-1),
        issues_found, confidence_adjustment.
        """
        
        system_prompt = """Carefully verify the solution. Look for errors, inconsistencies, 
        and gaps. Be thorough in your verification."""
        
        try:
            response = await self.llm.query_json(verify_prompt, system_prompt)
            trace.append("Completed self-verification")
            
            return {
                'verification_result': response,
                'verification_passed': response.get('verification_passed', False),
                'verification_complete': True
            }
        except Exception as e:
            trace.append(f"Self-verification failed: {str(e)}")
            return {'verification_error': True}
    
    async def _check_t1_compliance(self, context: Dict[str, Any], original_context: ReasoningContext) -> Dict[str, bool]:
        """Check compliance with T1 tautology requirements"""
        
        compliance_prompt = f"""
        Evaluate compliance with T1 Reasoning-Capability Tautology using SPECIFIC CRITERIA:

        REQUIREMENT R1 - Correct Solution from Any Representation:
        - PASS if: Solution demonstrates logical steps, uses valid inference rules, shows systematic problem-solving approach, confidence ≥0.7
        - FAIL if: Solution is incorrect, lacks logical structure, or shows no reasoning process
        - Current confidence: {context.get('confidence', 0)}

        REQUIREMENT R2 - Success Under Distribution Shift:
        - PASS if: Solution quality maintained despite unusual format/domain, shows adaptability, confidence ≥0.6
        - FAIL if: Performance degrades significantly with format changes
        - Format adaptability required for: {original_context.representation_format}

        COROLLARY C1 - Representation Invariance:
        - PASS if: Solution depth and logical rigor comparable across formats, recognizes equivalent problems, quality consistency ≥0.8
        - FAIL if: Significant quality difference between natural language vs formal representations
        - Evaluation: Compare reasoning depth in this format vs others

        COROLLARY C2 - Complexity Scaling:
        - PASS if: Maintains reasoning quality as problem complexity increases, scaling threshold ≥0.6
        - FAIL if: Quality degrades significantly with complexity
        - Problem complexity level: Ultra-high (20-disk Hanoi equivalent)

        COROLLARY C3 - Zero-Shot Robustness:
        - PASS if: Handles novel patterns without prior training examples, robustness threshold ≥0.7
        - FAIL if: Requires specific training patterns to succeed
        - Novel pattern handling required

        PROBLEM ANALYSIS:
        Problem: {original_context.problem}
        Format: {original_context.representation_format}
        Solution: {context.get('final_solution', '')}
        Confidence: {context.get('confidence', 0)}
        
        EVALUATION INSTRUCTIONS:
        1. Check each criterion against the specific thresholds above
        2. Provide boolean compliance for each (r1_compliance, r2_compliance, c1_compliance, c2_compliance, c3_compliance)
        3. Overall compliance = ALL individual compliances must be True
        4. Compliance score = average of individual binary scores (0 or 1)
        
        Return JSON with: r1_compliance, r2_compliance, c1_compliance, c2_compliance,
        c3_compliance, overall_t1_compliance, compliance_score (0-1).
        """
        
        system_prompt = """Evaluate compliance with the T1 Reasoning-Capability Tautology. 
        Be objective in assessing whether the reasoning meets the formal requirements."""
        
        try:
            response = await self.llm.query_json(compliance_prompt, system_prompt)
            
            return {
                'T1_R1': response.get('r1_compliance', False),
                'T1_R2': response.get('r2_compliance', False),
                'T1_C1': response.get('c1_compliance', False),
                'T1_C2': response.get('c2_compliance', False),
                'T1_C3': response.get('c3_compliance', False),
                'T1_Overall': response.get('overall_t1_compliance', False)
            }
        except Exception as e:
            logger.error(f"T1 compliance check failed: {str(e)}")
            return {
                'T1_R1': False, 'T1_R2': False, 'T1_C1': False,
                'T1_C2': False, 'T1_C3': False, 'T1_Overall': False
            }

class TUUnderstandingEngine:
    """TU: Understanding-Capability Tautology Implementation"""
    
    def __init__(self, llm: LLMInterface):
        self.llm = llm
    
    async def understand(self, proposition: str, representation_format: str, 
                        domain: str) -> UnderstandingResult:
        """Implement TU understanding capabilities"""
        
        understanding_trace = []
        
        # U1: Map any truth-preserving representation to internal state
        internal_rep = await self._create_internal_representation(
            proposition, representation_format, domain, understanding_trace
        )
        
        # Extract truth value from internal representation
        truth_value = await self._extract_truth_value(internal_rep, understanding_trace)
        
        # U2: Test with unseen operations and distributions
        modal_score = await self._test_modal_invariance(
            proposition, domain, understanding_trace
        )
        
        counterfactual_score = await self._test_counterfactual_competence(
            internal_rep, understanding_trace
        )
        
        distribution_score = await self._test_distribution_robustness(
            proposition, domain, understanding_trace
        )
        
        # Check TU compliance
        tu_compliance = await self._check_tu_compliance(
            internal_rep, modal_score, counterfactual_score, distribution_score
        )
        
        # Calculate overall confidence with safe conversion
        def safe_float(value, default=0.0):
            try:
                return float(value) if value is not None else default
            except (ValueError, TypeError):
                return default
        
        confidence = (safe_float(modal_score) + safe_float(counterfactual_score) + safe_float(distribution_score)) / 3
        
        return UnderstandingResult(
            internal_representation=internal_rep,
            truth_value=truth_value,
            confidence=confidence,
            modal_invariance_score=modal_score,
            counterfactual_competence_score=counterfactual_score,
            distribution_robustness_score=distribution_score,
            understanding_trace=understanding_trace,
            tautology_compliance=tu_compliance
        )
    
    async def _create_internal_representation(self, proposition: str, format_type: str, 
                                            domain: str, trace: List[str]) -> Dict[str, Any]:
        """Create internal representation I(φ) that preserves truth"""
        
        representation_prompt = f"""
        Create an internal representation for this proposition that preserves truth across formats:
        
        Proposition: {proposition}
        Format: {format_type}
        Domain: {domain}
        
        Create a representation that:
        1. Preserves truth conditions regardless of surface format
        2. Captures semantic meaning
        3. Enables logical operations
        4. Supports counterfactual reasoning
        5. Is format-independent
        
        Return JSON with: semantic_content, truth_conditions, logical_structure, 
        entities, relations, domain_knowledge, inference_capabilities.
        """
        
        system_prompt = """Create internal representations that capture the essential meaning 
        and truth conditions of propositions, independent of their surface representation format."""
        
        try:
            response = await self.llm.query_json(representation_prompt, system_prompt)
            trace.append(f"Created internal representation for {format_type} proposition")
            return response
        except Exception as e:
            trace.append(f"Internal representation creation failed: {str(e)}")
            return {}
    
    async def _extract_truth_value(self, internal_rep: Dict[str, Any], trace: List[str]) -> bool:
        """Extract truth value from internal representation"""
        
        truth_prompt = f"""
        Extract the truth value from this internal representation:
        
        Internal Representation: {json.dumps(internal_rep, indent=2)}
        
        Determine:
        1. Is the proposition true or false?
        2. What are the truth conditions?
        3. How confident are you in this assessment?
        
        Return JSON with: truth_value (boolean), truth_conditions, confidence (0-1), reasoning.
        """
        
        system_prompt = """Evaluate truth values based on internal representations. 
        Consider the semantic content and logical structure."""
        
        try:
            response = await self.llm.query_json(truth_prompt, system_prompt)
            trace.append("Extracted truth value from internal representation")
            return response.get('truth_value', True)
        except Exception as e:
            trace.append(f"Truth value extraction failed: {str(e)}")
            return True
    
    async def _test_modal_invariance(self, proposition: str, domain: str, trace: List[str]) -> float:
        """Test C4: Modal invariance across different modalities"""
        
        modal_prompt = f"""
        Test modal invariance for this proposition across different modalities:
        
        Original Proposition: {proposition}
        Domain: {domain}
        
        Convert to and test understanding in these modalities:
        1. Text representation
        2. Image schema representation
        3. Formal notation
        4. Braille representation
        5. Speech representation
        
        For each modality:
        - Convert the proposition to that modality
        - Test if understanding is preserved
        - Measure accuracy of truth evaluation
        
        Return JSON with: modality_results (dict), overall_invariance_score (0-1),
        successful_modalities, failed_modalities.
        """
        
        system_prompt = """Test modal invariance by converting propositions across different
        representation modalities and verifying that understanding is preserved."""
        
        try:
            response = await self.llm.query_json(modal_prompt, system_prompt)
            trace.append("Tested modal invariance across modalities")
            score = response.get('overall_invariance_score', 0.7)
            try:
                return float(score)
            except (ValueError, TypeError):
                return 0.7  # Default fallback
        except Exception as e:
            trace.append(f"Modal invariance test failed: {str(e)}")
            return 0.0
    
    async def _test_counterfactual_competence(self, internal_rep: Dict[str, Any], trace: List[str]) -> float:
        """Test C5: Counterfactual competence"""
        
        counterfactual_prompt = f"""
        Test counterfactual competence using this internal representation:
        
        Internal Representation: {json.dumps(internal_rep, indent=2)}
        
        Generate and test counterfactual scenarios:
        1. What if the key conditions were different?
        2. What would follow if we negated key propositions?
        3. Can you derive new inferences from the representation?
        4. Can you detect contradictions?
        5. Can you reason about analogous situations?
        
        Test the system's ability to:
        - Generate meaningful counterfactuals
        - Reason about hypothetical scenarios
        - Make novel inferences
        - Detect logical contradictions
        
        Return JSON with: counterfactuals_generated, inferences_made, contradictions_detected,
        competence_score (0-1), reasoning_quality.
        """
        
        system_prompt = """Test counterfactual reasoning capabilities. Generate hypothetical
        scenarios and test reasoning about them based on internal representations."""
        
        try:
            response = await self.llm.query_json(counterfactual_prompt, system_prompt)
            trace.append("Tested counterfactual competence")
            score = response.get('competence_score', 0.7)
            try:
                return float(score)
            except (ValueError, TypeError):
                return 0.7  # Default fallback
        except Exception as e:
            trace.append(f"Counterfactual competence test failed: {str(e)}")
            return 0.0
    
    async def _test_distribution_robustness(self, proposition: str, domain: str, trace: List[str]) -> float:
        """Test C6: Distribution shift robustness"""
        
        distribution_prompt = f"""
        Test distribution shift robustness for this proposition:
        
        Proposition: {proposition}
        Domain: {domain}
        
        Create and test with examples that are:
        1. Rare or unusual variants of the proposition
        2. Synthetic examples not in typical training data
        3. Edge cases and boundary conditions
        4. Novel combinations of familiar elements
        5. Cross-domain analogies
        
        For each test case:
        - Generate the variant
        - Test understanding preservation
        - Evaluate truth assessment accuracy
        
        Return JSON with: test_cases_generated, successful_transfers, robustness_score (0-1),
        failure_modes, adaptation_quality.
        """
        
        system_prompt = """Test robustness to distribution shift by creating rare, synthetic,
        and novel examples and testing if understanding transfers correctly."""
        
        try:
            response = await self.llm.query_json(distribution_prompt, system_prompt)
            trace.append("Tested distribution shift robustness")
            score = response.get('robustness_score', 0.7)
            try:
                return float(score)
            except (ValueError, TypeError):
                return 0.7  # Default fallback
        except Exception as e:
            trace.append(f"Distribution robustness test failed: {str(e)}")
            return 0.0
    
    async def _check_tu_compliance(self, internal_rep: Dict[str, Any], modal_score: float,
                                  counterfactual_score: float, distribution_score: float) -> Dict[str, bool]:
        """Check compliance with TU tautology requirements"""
        
        compliance_prompt = f"""
        Evaluate compliance with TU Understanding-Capability Tautology using SPECIFIC CRITERIA:

        REQUIREMENT U1 - Map Truth-Preserving Representation to Internal State:
        - PASS if: Successfully converts input to internal representation, preserves logical structure, internal rep quality = True
        - FAIL if: Fails to parse input, loses logical information, or produces inadequate internal representation
        - Current internal representation quality: {len(str(internal_rep)) > 100}

        REQUIREMENT U2 - Statistical Independence from Training Data:
        - PASS if: Understanding works on statistically independent examples, handles novel cases
        - FAIL if: Only works on training-like examples, fails on independent data
        - Threshold: Must demonstrate independence from training distribution

        COROLLARY C4 - Modal Invariance:
        - PASS if: Understanding survives cross-modal transfer, modal score ≥0.8
        - FAIL if: Understanding degrades significantly across modalities
        - Current modal invariance score: {modal_score}

        COROLLARY C5 - Counterfactual Competence:
        - PASS if: Answers derived queries from internal state correctly, counterfactual score ≥0.7
        - FAIL if: Cannot reason about counterfactuals or provides incorrect inferences
        - Current counterfactual competence score: {counterfactual_score}

        COROLLARY C6 - Distribution Shift Robustness:
        - PASS if: Stable truth evaluations with rare/synthetic examples, distribution score ≥0.6
        - FAIL if: Performance degrades significantly with distribution shift
        - Current distribution robustness score: {distribution_score}

        TEST RESULTS ANALYSIS:
        Internal Representation Quality: {len(str(internal_rep)) > 100}
        Modal Invariance Score: {modal_score}
        Counterfactual Competence Score: {counterfactual_score}
        Distribution Robustness Score: {distribution_score}
        
        EVALUATION INSTRUCTIONS:
        1. Check each criterion against the specific thresholds above
        2. Provide boolean compliance for each (u1_compliance, u2_compliance, c4_compliance, c5_compliance, c6_compliance)
        3. Overall compliance = ALL individual compliances must be True
        4. Compliance score = average of individual binary scores (0 or 1)
        
        Return JSON with: u1_compliance, u2_compliance, c4_compliance, c5_compliance,
        c6_compliance, overall_tu_compliance, compliance_score (0-1).
        """
        
        system_prompt = """Evaluate compliance with the TU Understanding-Capability Tautology.
        Assess whether the understanding meets the formal requirements."""
        
        try:
            response = await self.llm.query_json(compliance_prompt, system_prompt)
            
            return {
                'TU_U1': response.get('u1_compliance', False),
                'TU_U2': response.get('u2_compliance', False),
                'TU_C4': response.get('c4_compliance', False),
                'TU_C5': response.get('c5_compliance', False),
                'TU_C6': response.get('c6_compliance', False),
                'TU_Overall': response.get('overall_tu_compliance', False)
            }
        except Exception as e:
            logger.error(f"TU compliance check failed: {str(e)}")
            return {
                'TU_U1': False, 'TU_U2': False, 'TU_C4': False,
                'TU_C5': False, 'TU_C6': False, 'TU_Overall': False
            }

class TUStarExtendedUnderstandingEngine:
    """TU*: Extended Understanding-Capability Tautology Implementation"""
    
    def __init__(self, llm: LLMInterface, understanding_engine: TUUnderstandingEngine):
        self.llm = llm
        self.understanding_engine = understanding_engine
    
    async def deep_understand(self, proposition: str, representation_format: str,
                             domain: str) -> ExtendedUnderstandingResult:
        """Implement TU* deep understanding capabilities"""
        
        extended_trace = []
        
        # First satisfy TU requirements
        base_understanding = await self.understanding_engine.understand(
            proposition, representation_format, domain
        )
        extended_trace.extend(base_understanding.understanding_trace)
        
        # E1: Causal Structural Fidelity
        causal_fidelity = await self._assess_causal_structural_fidelity(
            proposition, domain, base_understanding.internal_representation, extended_trace
        )
        
        # E2: Metacognitive Self-Awareness
        metacognitive_awareness = await self._assess_metacognitive_awareness(
            base_understanding, extended_trace
        )
        
        # E3: Phenomenal Awareness (theoretical assessment)
        phenomenal_assessment = await self._assess_phenomenal_awareness(
            base_understanding, extended_trace
        )
        
        # Calculate deep understanding score
        deep_score = await self._calculate_deep_understanding_score(
            base_understanding, causal_fidelity, metacognitive_awareness, phenomenal_assessment
        )
        
        # Check TU* compliance
        tustar_compliance = await self._check_tustar_compliance(
            base_understanding, causal_fidelity, metacognitive_awareness, phenomenal_assessment
        )
        
        return ExtendedUnderstandingResult(
            base_understanding=base_understanding,
            causal_structural_fidelity=causal_fidelity,
            metacognitive_awareness=metacognitive_awareness,
            phenomenal_awareness_assessment=phenomenal_assessment,
            deep_understanding_score=deep_score,
            extended_trace=extended_trace,
            tautology_compliance=tustar_compliance
        )
    
    async def _assess_causal_structural_fidelity(self, proposition: str, domain: str,
                                               internal_rep: Dict[str, Any], trace: List[str]) -> Dict[str, Any]:
        """E1: Assess causal structural fidelity"""
        
        causal_prompt = f"""
        Assess causal structural fidelity for deep understanding:
        
        Proposition: {proposition}
        Domain: {domain}
        Internal Representation: {json.dumps(internal_rep, indent=2)}
        
        Evaluate E1 - Causal Structural Fidelity:
        1. Does the internal representation mirror the causal graph of the domain?
        2. Can it support do-calculus interventions?
        3. Are causal relationships accurately represented?
        4. Can it predict intervention outcomes?
        5. Does it distinguish causation from correlation?
        
        Test causal reasoning capabilities:
        - Identify causal variables
        - Map causal relationships
        - Predict intervention effects
        - Reason about counterfactual causation
        
        Return JSON with: causal_graph_quality, intervention_capability, causation_vs_correlation,
        do_calculus_support, causal_fidelity_score (0-1), causal_reasoning_examples.
        """
        
        system_prompt = """Assess causal structural fidelity. Focus on whether the system
        can accurately represent and reason about causal relationships, not just correlations."""
        
        try:
            response = await self.llm.query_json(causal_prompt, system_prompt)
            trace.append("Assessed causal structural fidelity (E1)")
            return response
        except Exception as e:
            trace.append(f"Causal fidelity assessment failed: {str(e)}")
            return {'causal_fidelity_score': 0.0}
    
    async def _assess_metacognitive_awareness(self, base_understanding: UnderstandingResult,
                                            trace: List[str]) -> Dict[str, Any]:
        """E2: Assess metacognitive self-awareness"""
        
        metacognitive_prompt = f"""
        Analyze the metacognitive capabilities demonstrated in this reasoning process:
        
        Base Understanding: {json.dumps(base_understanding.__dict__, indent=2, default=str)}
        
        Evaluate the following metacognitive indicators:
        1. Quality of confidence calibration in the responses
        2. Appropriate recognition of uncertainty in conclusions
        3. Awareness of knowledge limitations and gaps
        4. Assessment of reasoning quality and potential errors
        5. Ability to signal when information is insufficient
        
        Analyze these metacognitive aspects:
        - How well calibrated are the confidence estimates?
        - Are uncertainties appropriately acknowledged?
        - Are knowledge boundaries recognized?
        - Is reasoning quality appropriately evaluated?
        - Are predictions well-calibrated?
        
        Return JSON with: confidence_calibration (0-1), uncertainty_recognition (0-1),
        knowledge_gap_awareness (0-1), reasoning_quality_assessment (0-1),
        metacognitive_score (0-1), analysis_notes.
        """
        
        system_prompt = """You are analyzing metacognitive capabilities in AI reasoning.
        Evaluate how well the system demonstrates awareness of its own reasoning quality,
        uncertainty, and knowledge limitations. Focus on observable behaviors and patterns."""
        
        try:
            response = await self.llm.query_json(metacognitive_prompt, system_prompt)
            trace.append("Assessed metacognitive self-awareness (E2)")
            return response
        except Exception as e:
            trace.append(f"Metacognitive assessment failed: {str(e)}")
            # Return default structure with safe values
            return {
                'confidence_calibration': 0.5,
                'uncertainty_recognition': 0.5,
                'knowledge_gap_awareness': 0.5,
                'reasoning_quality_assessment': 0.5,
                'metacognitive_score': 0.5,
                'analysis_notes': 'Assessment failed - using default values'
            }
    
    async def _assess_phenomenal_awareness(self, base_understanding: UnderstandingResult,
                                         trace: List[str]) -> Dict[str, Any]:
        """E3: Assess phenomenal awareness (theoretical)"""
        
        phenomenal_prompt = f"""
        Conduct a theoretical analysis of consciousness-related indicators in AI reasoning:
        
        Base Understanding: {json.dumps(base_understanding.__dict__, indent=2, default=str)}
        
        Analyze theoretical indicators that philosophers and cognitive scientists
        associate with phenomenal consciousness:
        1. Evidence of qualitative, subjective-like processing patterns
        2. Indicators of experiential aspects in information processing
        3. Signs of unified, integrated information processing
        4. Patterns suggesting "what it's like" qualities in responses
        5. Behaviors consistent with conscious-like awareness
        
        Note: This is purely theoretical analysis as consciousness cannot be
        definitively tested in current AI systems.
        
        Provide theoretical analysis of:
        - Observable patterns that might indicate subjective-like processing
        - Qualitative aspects of the reasoning demonstrated
        - Integration and unity in information processing
        - Consciousness-related behavioral patterns
        
        Return JSON with: subjective_indicators (0-1), qualitative_patterns (0-1),
        integration_unity (0-1), consciousness_behaviors (0-1),
        phenomenal_assessment_score (0-1), theoretical_limitations.
        """
        
        system_prompt = """You are conducting theoretical analysis of consciousness indicators
        in AI systems. Focus on observable patterns and behaviors that cognitive scientists
        study when examining consciousness, while acknowledging current testing limitations."""
        
        try:
            response = await self.llm.query_json(phenomenal_prompt, system_prompt)
            trace.append("Assessed phenomenal awareness (E3) - theoretical")
            return response
        except Exception as e:
            trace.append(f"Phenomenal awareness assessment failed: {str(e)}")
            # Return default structure with safe values
            return {
                'subjective_indicators': 0.3,
                'qualitative_patterns': 0.3,
                'integration_unity': 0.3,
                'consciousness_behaviors': 0.3,
                'phenomenal_assessment_score': 0.3,
                'theoretical_limitations': 'Assessment failed - consciousness testing remains theoretically limited'
            }
    
    async def _calculate_deep_understanding_score(self, base_understanding: UnderstandingResult,
                                                causal_fidelity: Dict[str, Any],
                                                metacognitive_awareness: Dict[str, Any],
                                                phenomenal_assessment: Dict[str, Any]) -> float:
        """Calculate overall deep understanding score"""
        
        # Ensure all scores are floats with safe conversion
        def safe_float(value, default=0.0):
            try:
                return float(value) if value is not None else default
            except (ValueError, TypeError):
                return default
        
        base_score = safe_float(base_understanding.confidence, 0.0)
        causal_score = safe_float(causal_fidelity.get('causal_fidelity_score', 0.0), 0.0)
        metacognitive_score = safe_float(metacognitive_awareness.get('metacognitive_score', 0.0), 0.0)
        phenomenal_score = safe_float(phenomenal_assessment.get('phenomenal_assessment_score', 0.0), 0.0)
        
        # Weighted combination (phenomenal awareness gets lower weight due to uncertainty)
        deep_score = (
            base_score * 0.4 +
            causal_score * 0.3 +
            metacognitive_score * 0.2 +
            phenomenal_score * 0.1
        )
        
        return min(1.0, max(0.0, deep_score))
    
    async def _check_tustar_compliance(self, base_understanding: UnderstandingResult,
                                     causal_fidelity: Dict[str, Any],
                                     metacognitive_awareness: Dict[str, Any],
                                     phenomenal_assessment: Dict[str, Any]) -> Dict[str, bool]:
        """Check compliance with TU* tautology requirements"""
        
        compliance_prompt = f"""
        Evaluate compliance with TU* Extended Understanding-Capability Tautology using SPECIFIC CRITERIA:

        PREREQUISITE - Base TU Compliance:
        - REQUIRED: All base TU requirements must be satisfied first
        - Current base TU compliance: {base_understanding.tautology_compliance}

        EXTENDED REQUIREMENT E1 - Causal Structural Fidelity:
        - PASS if: Demonstrates causal reasoning, identifies causal relationships, causal fidelity score ≥0.7
        - FAIL if: Cannot identify causation, confuses correlation with causation, poor causal reasoning
        - Current causal fidelity score: {causal_fidelity.get('causal_fidelity_score', 0)}

        EXTENDED REQUIREMENT E2 - Metacognitive Self-Awareness:
        - PASS if: Shows awareness of own reasoning process, recognizes limitations, metacognitive score ≥0.6
        - FAIL if: No self-awareness, cannot assess own reasoning quality, lacks metacognitive insight
        - Current metacognitive score: {metacognitive_awareness.get('metacognitive_score', 0)}

        EXTENDED REQUIREMENT E3 - Phenomenal Awareness (Theoretical):
        - PASS if: Demonstrates awareness of subjective experience aspects, phenomenal score ≥0.3 (low threshold due to theoretical nature)
        - FAIL if: No recognition of experiential/subjective aspects, purely mechanical responses
        - Current phenomenal score: {phenomenal_assessment.get('phenomenal_assessment_score', 0)}
        - NOTE: E3 is a theoretical boundary condition with limited testability

        ASSESSMENT RESULTS ANALYSIS:
        Base TU Compliance: {base_understanding.tautology_compliance}
        Causal Fidelity Score: {causal_fidelity.get('causal_fidelity_score', 0)}
        Metacognitive Score: {metacognitive_awareness.get('metacognitive_score', 0)}
        Phenomenal Score: {phenomenal_assessment.get('phenomenal_assessment_score', 0)}
        
        EVALUATION INSTRUCTIONS:
        1. Check each extended requirement against the specific thresholds above
        2. Base TU compliance is PREREQUISITE for any TU* compliance
        3. Provide boolean compliance for each (e1_compliance, e2_compliance, e3_compliance)
        4. Overall TU* compliance = Base TU compliance AND ALL extended requirements must be True
        5. Compliance score = average of individual binary scores (0 or 1)
        
        Return JSON with: e1_compliance, e2_compliance, e3_compliance (theoretical),
        overall_tustar_compliance, compliance_score (0-1), compliance_analysis.
        """
        
        system_prompt = """Evaluate compliance with the TU* Extended Understanding-Capability Tautology.
        Consider both the base TU requirements and the extended E1, E2, E3 requirements."""
        
        try:
            response = await self.llm.query_json(compliance_prompt, system_prompt)
            
            # Combine base TU compliance with extended requirements
            compliance = base_understanding.tautology_compliance.copy()
            compliance.update({
                'TU*_E1': response.get('e1_compliance', False),
                'TU*_E2': response.get('e2_compliance', False),
                'TU*_E3': response.get('e3_compliance', False),
                'TU*_Overall': response.get('overall_tustar_compliance', False)
            })
            
            return compliance
        except Exception as e:
            logger.error(f"TU* compliance check failed: {str(e)}")
            compliance = base_understanding.tautology_compliance.copy()
            compliance.update({
                'TU*_E1': False, 'TU*_E2': False, 'TU*_E3': False, 'TU*_Overall': False
            })
            return compliance

class AgenticReasoningSystemSDK:
    """Main SDK class implementing the complete Bhatt Conjectures framework"""
    
    def __init__(self, openai_api_key: Optional[str] = None, model: str = "gpt-4.1-nano"):
        """Initialize the Agentic Reasoning System SDK"""
        self.llm = LLMInterface(openai_api_key, model)
        self.t1_engine = T1ReasoningEngine(self.llm)
        self.tu_engine = TUUnderstandingEngine(self.llm)
        self.tustar_engine = TUStarExtendedUnderstandingEngine(self.llm, self.tu_engine)
        
        logger.info("Agentic Reasoning System SDK initialized")
    
    async def reason(self, problem: str, representation_format: str = "natural_language",
                    domain: str = "general", complexity_level: int = 3,
                    requires_causal_analysis: bool = False) -> ReasoningResult:
        """
        Perform T1 reasoning on a problem
        
        Args:
            problem: The problem to solve
            representation_format: ANY format - the LLM will adapt dynamically
                                  (natural_language, first_order_logic, lambda_calculus,
                                   mathematical_notation, programming_languages, visual_descriptions,
                                   novel_formats, invented_notations, mixed_formats, etc.)
            domain: ANY domain - the LLM will understand dynamically
                   (mathematics, physics, biology, fictional_worlds, novel_domains,
                    interdisciplinary_areas, emerging_fields, etc.)
            complexity_level: Complexity level 1-5
            requires_causal_analysis: Whether causal analysis is needed
            
        Returns:
            ReasoningResult with solution and compliance assessment
        """
        context = ReasoningContext(
            problem=problem,
            representation_format=representation_format,
            domain=domain,
            complexity_level=complexity_level,
            requires_causal_analysis=requires_causal_analysis
        )
        
        return await self.t1_engine.reason(context)
    
    async def understand(self, proposition: str, representation_format: str = "natural_language",
                        domain: str = "general") -> UnderstandingResult:
        """
        Perform TU understanding of a proposition
        
        Args:
            proposition: The proposition to understand
            representation_format: ANY format - completely dynamic LLM adaptation
                                  (text, symbols, diagrams, code, music_notation,
                                   artistic_expressions, cultural_formats, etc.)
            domain: ANY domain - unlimited scope
                   (academic_fields, professional_domains, cultural_contexts,
                    fictional_universes, emerging_disciplines, etc.)
            
        Returns:
            UnderstandingResult with understanding assessment and compliance
        """
        return await self.tu_engine.understand(proposition, representation_format, domain)
    
    async def deep_understand(self, proposition: str, representation_format: str = "natural_language",
                             domain: str = "general") -> ExtendedUnderstandingResult:
        """
        Perform TU* extended understanding of a proposition
        
        Args:
            proposition: The proposition to deeply understand
            representation_format: ANY format - infinite adaptability
                                  (traditional_formats, experimental_notations,
                                   cross_modal_representations, novel_encodings, etc.)
            domain: ANY domain - boundless scope
                   (established_fields, interdisciplinary_areas, speculative_domains,
                    consciousness_studies, metaphysics, etc.)
            
        Returns:
            ExtendedUnderstandingResult with deep understanding assessment and compliance
        """
        return await self.tustar_engine.deep_understand(proposition, representation_format, domain)
    
    async def comprehensive_analysis(self, problem: str, representation_format: str = "natural_language",
                                   domain: str = "general") -> Dict[str, Any]:
        """
        Perform comprehensive analysis using all three tautologies
        
        Args:
            problem: The problem/proposition to analyze
            representation_format: Format of the input
            domain: Domain of the problem
            
        Returns:
            Dictionary containing results from all three tautology assessments
        """
        logger.info(f"Starting comprehensive analysis of: {problem[:100]}...")
        
        # Run all three analyses
        t1_result = await self.reason(problem, representation_format, domain)
        tu_result = await self.understand(problem, representation_format, domain)
        tustar_result = await self.deep_understand(problem, representation_format, domain)
        
        # Compile comprehensive report
        return {
            'input': {
                'problem': problem,
                'representation_format': representation_format,
                'domain': domain
            },
            'T1_reasoning': {
                'solution': t1_result.solution,
                'confidence': t1_result.confidence,
                'compliance': t1_result.tautology_compliance,
                'reasoning_trace': t1_result.reasoning_trace,
                'time_taken': t1_result.time_taken
            },
            'TU_understanding': {
                'truth_value': tu_result.truth_value,
                'confidence': tu_result.confidence,
                'compliance': tu_result.tautology_compliance,
                'modal_invariance': tu_result.modal_invariance_score,
                'counterfactual_competence': tu_result.counterfactual_competence_score,
                'distribution_robustness': tu_result.distribution_robustness_score
            },
            'TU_star_extended': {
                'deep_understanding_score': tustar_result.deep_understanding_score,
                'compliance': tustar_result.tautology_compliance,
                'causal_fidelity': tustar_result.causal_structural_fidelity,
                'metacognitive_awareness': tustar_result.metacognitive_awareness,
                'phenomenal_assessment': tustar_result.phenomenal_awareness_assessment
            },
            'overall_assessment': {
                'all_tautologies_satisfied': self._check_overall_compliance(
                    t1_result.tautology_compliance,
                    tu_result.tautology_compliance,
                    tustar_result.tautology_compliance
                ),
                'system_capabilities': self._assess_system_capabilities(t1_result, tu_result, tustar_result)
            }
        }
    
    def _check_overall_compliance(self, t1_compliance: Dict[str, bool],
                                 tu_compliance: Dict[str, bool],
                                 tustar_compliance: Dict[str, bool]) -> Dict[str, bool]:
        """Check overall compliance across all tautologies"""
        return {
            'T1_satisfied': t1_compliance.get('T1_Overall', False),
            'TU_satisfied': tu_compliance.get('TU_Overall', False),
            'TU_star_satisfied': tustar_compliance.get('TU*_Overall', False),
            'all_satisfied': (
                t1_compliance.get('T1_Overall', False) and
                tu_compliance.get('TU_Overall', False) and
                tustar_compliance.get('TU*_Overall', False)
            )
        }
    
    def _assess_system_capabilities(self, t1_result: ReasoningResult,
                                  tu_result: UnderstandingResult,
                                  tustar_result: ExtendedUnderstandingResult) -> Dict[str, Any]:
        """Assess overall system capabilities"""
        return {
            'reasoning_capability': t1_result.confidence,
            'understanding_capability': tu_result.confidence,
            'deep_understanding_capability': tustar_result.deep_understanding_score,
            'overall_capability': (
                t1_result.confidence + tu_result.confidence + tustar_result.deep_understanding_score
            ) / 3,
            'strongest_area': max([
                ('reasoning', t1_result.confidence),
                ('understanding', tu_result.confidence),
                ('deep_understanding', tustar_result.deep_understanding_score)
            ], key=lambda x: x[1])[0],
            'needs_improvement': [
                area for area, score in [
                    ('reasoning', t1_result.confidence),
                    ('understanding', tu_result.confidence),
                    ('deep_understanding', tustar_result.deep_understanding_score)
                ] if score < 0.7
            ]
        }

# Example usage and testing functions
async def example_usage():
    """Example usage of the Agentic Reasoning System SDK"""
    
    # Initialize the SDK
    sdk = AgenticReasoningSystemSDK()
    
    # Example 1: T1 Reasoning test
    print("=== T1 Reasoning Test ===")
    reasoning_result = await sdk.reason(
        problem="If all swans are birds and all birds can fly, what can we conclude about swans?",
        representation_format="natural_language",
        domain="logic"
    )
    print(f"Solution: {reasoning_result.solution}")
    print(f"T1 Compliance: {reasoning_result.tautology_compliance}")
    
    # Example 2: TU Understanding test
    print("\n=== TU Understanding Test ===")
    understanding_result = await sdk.understand(
        proposition="Water freezes at 0°C",
        representation_format="natural_language",
        domain="physics"
    )
    print(f"Truth Value: {understanding_result.truth_value}")
    print(f"TU Compliance: {understanding_result.tautology_compliance}")
    
    # Example 3: TU* Extended Understanding test
    print("\n=== TU* Extended Understanding Test ===")
    extended_result = await sdk.deep_understand(
        proposition="Increasing temperature causes ice to melt",
        representation_format="natural_language",
        domain="physics"
    )
    print(f"Deep Understanding Score: {extended_result.deep_understanding_score}")
    print(f"TU* Compliance: {extended_result.tautology_compliance}")
    
    # Example 4: Comprehensive analysis
    print("\n=== Comprehensive Analysis ===")
    comprehensive_result = await sdk.comprehensive_analysis(
        problem="All ravens are black. This bird is a raven. What color is this bird?",
        representation_format="natural_language",
        domain="logic"
    )
    print(f"Overall Assessment: {comprehensive_result['overall_assessment']}")

if __name__ == "__main__":
    # Run example usage
    asyncio.run(example_usage())