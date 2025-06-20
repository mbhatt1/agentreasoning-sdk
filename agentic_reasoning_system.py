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
# Try to import config, provide fallbacks if not available
try:
    from config import PERFORMANCE_CONFIG, COMPLIANCE_THRESHOLDS, STATE_MACHINE_CONFIG, VALIDATION_RULES
except ImportError:
    # Fallback configurations if config.py is not available
    PERFORMANCE_CONFIG = {
        'json_parsing_retries': 3,
        'json_retry_temperature_increment': 0.2,
        'json_retry_delay': 0.2
    }
    COMPLIANCE_THRESHOLDS = {}
    STATE_MACHINE_CONFIG = {}
    VALIDATION_RULES = {}

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ReasoningMode(Enum):
    """Different modes of reasoning based on Fast/Slow thinking"""
    FAST_INTUITIVE = "fast_intuitive"
    SLOW_DELIBERATIVE = "slow_deliberative"
    METACOGNITIVE = "metacognitive"
    CAUSAL = "causal"
    HYBRID_ADAPTIVE = "hybrid_adaptive"  # New: Dynamic switching between fast/slow
    ULTRA_COMPLEX = "ultra_complex"      # New: For 20-disk Hanoi level problems

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
    hanoi_disc_count: int = 0  # New: Track Tower of Hanoi complexity
    exponential_operations: int = 0  # New: Track exponential complexity (2^n operations)
    is_ultra_complex: bool = False  # New: Flag for 20-disk level problems
    fast_slow_switching_enabled: bool = True  # New: Enable dynamic mode switching
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ReasoningResult:
    """Result of reasoning operation"""
    success: bool
    solution: str
    confidence: float
    reasoning_trace: List[str]
    state_transitions: List[Dict[str, Any]]
    processing_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    # Legacy fields for backward compatibility
    internal_state: Dict[str, Any] = field(default_factory=dict)
    mode_used: ReasoningMode = ReasoningMode.SLOW_DELIBERATIVE
    time_taken: float = 0.0
    uncertainty_estimate: float = 0.0
    causal_graph: Optional[Dict] = None
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
    processing_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    tautology_compliance: Dict[str, bool] = field(default_factory=dict)

@dataclass
class ExtendedUnderstandingResult:
    """Result of extended understanding operation (TU*)"""
    base_understanding: UnderstandingResult
    causal_structural_fidelity: Dict[str, Any]
    metacognitive_awareness: Dict[str, Any]
    phenomenal_awareness: Dict[str, Any]
    deep_understanding_score: float
    extended_understanding_trace: List[str]
    processing_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    tautology_compliance: Dict[str, bool] = field(default_factory=dict)

class LLMInterface:
    """Interface to OpenAI's LLM for all reasoning tasks"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "o3"):
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable or pass api_key parameter.")
        self.client = openai.OpenAI(api_key=api_key)
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
        """Query LLM and expect JSON response with robust parsing and retry logic"""
        max_retries = PERFORMANCE_CONFIG.get('json_parsing_retries', 4)
        retry_delay = PERFORMANCE_CONFIG.get('json_retry_delay', 0.5)
        
        for attempt in range(max_retries + 1):
            try:
                # Progressively more explicit JSON prompts
                if attempt == 0:
                    json_prompt = f"{prompt}\n\nIMPORTANT: Respond with valid JSON only. Start with {{ and end with }}. No additional text."
                elif attempt == 1:
                    json_prompt = f"{prompt}\n\nCRITICAL: Return ONLY valid JSON. No explanations, no markdown, no code blocks. Just pure JSON starting with {{ and ending with }}. Example format: {{\"key\": \"value\", \"number\": 0.5}}"
                elif attempt == 2:
                    json_prompt = f"{prompt}\n\nJSON ONLY: Return a complete, valid JSON object. Ensure all braces are closed. No truncation allowed. Use double quotes for all strings. End with }}"
                elif attempt == 3:
                    json_prompt = f"{prompt}\n\nSTRICT JSON: Must be parseable by json.loads(). Format: {{\"field1\": \"value1\", \"field2\": 0.5, \"field3\": true}}. No trailing commas. No comments. Complete object only."
                else:
                    json_prompt = f"{prompt}\n\nFINAL ATTEMPT - PURE JSON: Return ONLY a valid JSON object that can be parsed by Python's json.loads(). No text before or after. Start with {{ and end with }}. Use double quotes for strings. No trailing commas."
                
                # Increase max tokens for later attempts to avoid truncation
                max_tokens = 2000 + (attempt * 1000)  # 2000, 3000, 4000, 5000, 6000
                
                # O3 model only supports temperature=1, so don't increment
                response = await self.query(json_prompt, system_prompt, 1.0, max_tokens)
                
                # Log the raw response for debugging (truncated)
                logger.debug(f"Attempt {attempt+1} raw response (first 200 chars): {response[:200]}")
                
                # Enhanced parsing strategies for robust JSON parsing
                parsing_strategies = [
                    # Strategy 1: Try parsing response as-is (most common case)
                    lambda r: json.loads(r.strip()),
                    # Strategy 2: Extract first complete JSON object
                    lambda r: self._extract_json_object(r),
                    # Strategy 3: Clean and parse entire response
                    lambda r: json.loads(self._clean_json_response(r)),
                    # Strategy 4: Extract content between code blocks
                    lambda r: self._extract_from_code_blocks(r),
                    # Strategy 5: Try to fix common JSON issues
                    lambda r: self._fix_and_parse_json(r),
                    # Strategy 6: Extract JSON from mixed content
                    lambda r: self._extract_json_from_mixed_content(r),
                    # Strategy 7: Try parsing with relaxed JSON
                    lambda r: self._parse_relaxed_json(r),
                    # Strategy 8: Try parsing with different whitespace handling
                    lambda r: json.loads(r.replace('\n', ' ').replace('\t', ' ').strip()),
                ]
                
                for i, strategy in enumerate(parsing_strategies):
                    try:
                        result = strategy(response)
                        if isinstance(result, dict) and result:  # Ensure non-empty dict
                            logger.debug(f"JSON parsing succeeded with strategy {i+1} on attempt {attempt+1}")
                            return result
                    except (json.JSONDecodeError, ValueError, AttributeError, TypeError) as e:
                        logger.debug(f"JSON parsing strategy {i+1} failed on attempt {attempt+1}: {str(e)}")
                        continue
                
                # If we get here, all strategies failed for this attempt
                logger.warning(f"All JSON parsing strategies failed on attempt {attempt+1}")
                logger.warning(f"Response that failed to parse: {response[:300]}...")
                
                if attempt < max_retries:
                    logger.info(f"Retrying JSON parsing (attempt {attempt+2}/{max_retries+1})...")
                    await asyncio.sleep(retry_delay)
                    continue
                else:
                    # Instead of fallback, make LLM regenerate the JSON
                    logger.warning(f"All JSON parsing attempts failed after {max_retries+1} attempts")
                    logger.warning(f"Final response: {response[:500]}...")
                    logger.info("Requesting LLM to regenerate JSON response...")
                    
                    # Create a regeneration prompt
                    regeneration_prompt = f"""
                    The previous response could not be parsed as valid JSON. Please regenerate your response as PURE, VALID JSON only.
                    
                    Original prompt was: {prompt}
                    
                    Your previous response was: {response[:200]}...
                    
                    CRITICAL REQUIREMENTS:
                    1. Return ONLY valid JSON - no explanations, no markdown, no code blocks
                    2. Start with {{ and end with }}
                    3. Use double quotes for all strings
                    4. No trailing commas
                    5. Ensure all braces are properly closed
                    6. Include all required fields from the original prompt
                    
                    Regenerate the response as pure JSON:
                    """
                    
                    try:
                        # Make one final attempt with regeneration prompt
                        regenerated_response = await self.query(regeneration_prompt, system_prompt, 1.0, 3000)
                        logger.info(f"LLM regenerated response (first 200 chars): {regenerated_response[:200]}")
                        
                        # Try to parse the regenerated response
                        try:
                            result = json.loads(regenerated_response.strip())
                            if isinstance(result, dict) and result:
                                logger.info("Successfully parsed regenerated JSON response")
                                return result
                        except json.JSONDecodeError:
                            logger.warning("Regenerated response also failed JSON parsing")
                        
                        # If regeneration also fails, try extraction strategies on regenerated response
                        for i, strategy in enumerate([
                            lambda r: self._extract_json_object(r),
                            lambda r: json.loads(self._clean_json_response(r)),
                            lambda r: self._fix_and_parse_json(r)
                        ]):
                            try:
                                result = strategy(regenerated_response)
                                if isinstance(result, dict) and result:
                                    logger.info(f"Regenerated response parsed with strategy {i+1}")
                                    return result
                            except:
                                continue
                                
                    except Exception as e:
                        logger.error(f"JSON regeneration attempt failed: {str(e)}")
                    
                    # Only use fallback as absolute last resort
                    logger.error("All JSON regeneration attempts failed - using fallback")
                    return self._create_fallback_response(response)
                    
            except Exception as e:
                logger.error(f"Query attempt {attempt+1} failed with exception: {str(e)}")
                if attempt < max_retries:
                    await asyncio.sleep(retry_delay)
                    continue
                else:
                    # Try regeneration for query failures too
                    logger.warning(f"All query attempts failed after {max_retries+1} attempts")
                    logger.info("Attempting JSON regeneration for query failure...")
                    
                    try:
                        regeneration_prompt = f"""
                        Previous attempts to respond failed. Please provide a valid JSON response to this prompt:
                        
                        {prompt}
                        
                        CRITICAL: Return ONLY valid JSON. Start with {{ and end with }}. No explanations.
                        """
                        
                        regenerated_response = await self.query(regeneration_prompt, system_prompt, 1.0, 2000)
                        result = json.loads(regenerated_response.strip())
                        if isinstance(result, dict) and result:
                            logger.info("Successfully regenerated JSON after query failures")
                            return result
                    except Exception as regen_e:
                        logger.error(f"JSON regeneration after query failure failed: {str(regen_e)}")
                    
                    return self._create_fallback_response(f"Query failed: {str(e)}")
        
        # Should never reach here, but just in case
        logger.error("Maximum retries exceeded - attempting final regeneration")
        try:
            final_regeneration_prompt = f"""
            Provide a valid JSON response to: {prompt}
            
            Return ONLY valid JSON starting with {{ and ending with }}.
            """
            final_response = await self.query(final_regeneration_prompt, system_prompt, 1.0, 2000)
            result = json.loads(final_response.strip())
            if isinstance(result, dict) and result:
                logger.info("Final regeneration attempt succeeded")
                return result
        except Exception as final_e:
            logger.error(f"Final regeneration attempt failed: {str(final_e)}")
        
        return self._create_fallback_response("Maximum retries exceeded")
    
    def _extract_json_object(self, response: str) -> Dict[str, Any]:
        """Extract the first complete JSON object from response with proper escape handling"""
        # Find the first opening brace
        start_idx = response.find('{')
        if start_idx == -1:
            raise ValueError("No JSON object found")
        
        # Track brace nesting to find the complete object
        brace_count = 0
        in_string = False
        i = start_idx
        
        while i < len(response):
            char = response[i]
            
            if in_string:
                # Handle escape sequences properly
                if char == '\\':
                    # Skip the next character (it's escaped)
                    i += 2
                    continue
                elif char == '"':
                    # End of string
                    in_string = False
            else:
                # Not in string
                if char == '"':
                    # Start of string
                    in_string = True
                elif char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        # Found complete JSON object
                        json_str = response[start_idx:i+1]
                        try:
                            return json.loads(json_str)
                        except json.JSONDecodeError as e:
                            # Try to fix common issues before giving up
                            try:
                                fixed_json = self._fix_json_string(json_str)
                                return json.loads(fixed_json)
                            except json.JSONDecodeError:
                                # If fixing fails, try more aggressive fixes
                                return self._aggressive_json_fix(json_str)
            
            i += 1
        
        raise ValueError("Incomplete JSON object - no matching closing brace found")
    
    def _fix_json_string(self, json_str: str) -> str:
        """Fix common JSON string issues with proper escaping handling"""
        import re
        
        # 1. Remove trailing commas before closing braces/brackets
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
        
        # 2. Handle single quotes to double quotes conversion carefully
        # First, protect already escaped quotes
        json_str = json_str.replace('\\"', '___ESCAPED_QUOTE___')
        json_str = json_str.replace("\\'", '___ESCAPED_SINGLE_QUOTE___')
        
        # Convert single-quoted strings to double-quoted strings
        # This handles both keys and values
        def convert_single_quoted_strings(text):
            result = ""
            i = 0
            while i < len(text):
                if text[i] == "'":
                    # Found start of single-quoted string
                    start = i
                    i += 1
                    # Find the end of the string
                    while i < len(text) and text[i] != "'":
                        if text[i] == '\\':
                            i += 2  # Skip escaped character
                        else:
                            i += 1
                    
                    if i < len(text):  # Found closing quote
                        # Extract content and convert to double quotes
                        content = text[start+1:i]
                        # Escape any double quotes in the content
                        content = content.replace('"', '\\"')
                        result += f'"{content}"'
                        i += 1
                    else:
                        # No closing quote found, just add the single quote
                        result += text[start]
                        i = start + 1
                else:
                    result += text[i]
                    i += 1
            return result
        
        json_str = convert_single_quoted_strings(json_str)
        
        # 3. Fix missing quotes around keys (but preserve already quoted keys)
        json_str = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*:)', r'\1"\2"\3', json_str)
        
        # 4. Restore escaped quotes
        json_str = json_str.replace('___ESCAPED_QUOTE___', '\\"')
        json_str = json_str.replace('___ESCAPED_SINGLE_QUOTE___', "'")
        
        # 5. Fix improperly escaped quotes in string values
        def fix_inner_quotes(match):
            key_part = match.group(1)
            value_part = match.group(2)
            end_part = match.group(3)
            
            # Escape any unescaped quotes in the value part
            fixed_value = re.sub(r'(?<!\\)"', '\\"', value_part)
            return f'{key_part}"{fixed_value}"{end_part}'
        
        # Apply the fix for unescaped quotes in string values
        json_str = re.sub(r'(:\s*")([^"]*)"(\s*[,}\]])', fix_inner_quotes, json_str)
        
        return json_str
    
    def _aggressive_json_fix(self, json_str: str) -> Dict[str, Any]:
        """Aggressive JSON fixing for severely malformed JSON"""
        import re
        
        # Start with basic cleaning
        cleaned = json_str.strip()
        
        # Remove any text before first { and after last }
        start = cleaned.find('{')
        end = cleaned.rfind('}')
        if start != -1 and end != -1 and end > start:
            cleaned = cleaned[start:end+1]
        
        # Fix common escaping issues
        # 1. Fix double escaping
        cleaned = cleaned.replace('\\\\', '\\')
        
        # 2. Fix unescaped newlines in strings
        cleaned = re.sub(r'(?<!\\)\n', '\\n', cleaned)
        cleaned = re.sub(r'(?<!\\)\r', '\\r', cleaned)
        cleaned = re.sub(r'(?<!\\)\t', '\\t', cleaned)
        
        # 3. Fix unescaped quotes in string values
        def fix_string_content(match):
            key = match.group(1)
            value = match.group(2)
            # Escape any unescaped quotes in the value
            fixed_value = re.sub(r'(?<!\\)"', '\\"', value)
            return f'"{key}": "{fixed_value}"'
        
        # Apply string content fixing
        cleaned = re.sub(r'"([^"]+)":\s*"([^"]*(?:\\.[^"]*)*)"', fix_string_content, cleaned)
        
        # 4. Remove trailing commas
        cleaned = re.sub(r',(\s*[}\]])', r'\1', cleaned)
        
        # 5. Fix missing quotes around keys
        cleaned = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*:)', r'\1"\2"\3', cleaned)
        
        # 6. Fix boolean and null values that might be quoted
        cleaned = re.sub(r':\s*"(true|false|null)"\s*([,}\]])', r': \1\2', cleaned)
        
        # 7. Fix numbers that might be quoted
        cleaned = re.sub(r':\s*"(\d+\.?\d*)"(\s*[,}\]])', r': \1\2', cleaned)
        
        # 8. Handle incomplete JSON by adding missing closing braces
        open_braces = cleaned.count('{')
        close_braces = cleaned.count('}')
        if open_braces > close_braces:
            cleaned += '}' * (open_braces - close_braces)
        
        # 9. Remove incomplete key-value pairs at the end
        lines = cleaned.split('\n')
        for i in range(len(lines) - 1, -1, -1):
            line = lines[i].strip()
            if line and ':' in line and not line.endswith((',', '}', ']')):
                # Remove incomplete line
                lines = lines[:i]
                break
        
        cleaned = '\n'.join(lines)
        if not cleaned.endswith('}'):
            cleaned += '}'
        
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Final fallback: create a minimal valid JSON
            return {
                "error": "json_parsing_failed",
                "original_content": json_str[:100],
                "confidence": 0.0,
                "solution": "Failed to parse JSON response"
            }
    
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
            "```",
            "Here is the JSON:",
            "The JSON is:",
            "JSON:",
        ]
        
        for prefix in prefixes_to_remove:
            if response.lower().startswith(prefix.lower()):
                response = response[len(prefix):].strip()
        
        # Remove common suffixes
        suffixes_to_remove = [
            "```",
            "That's the JSON response.",
            "This is the JSON.",
        ]
        
        for suffix in suffixes_to_remove:
            if response.lower().endswith(suffix.lower()):
                response = response[:-len(suffix)].strip()
        
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
    
    def _fix_and_parse_json(self, response: str) -> Dict[str, Any]:
        """Fix common JSON issues and parse with proper escaping handling"""
        import re
        
        # Clean the response
        cleaned = response.strip()
        
        # Remove any text before the first {
        start_idx = cleaned.find('{')
        if start_idx > 0:
            cleaned = cleaned[start_idx:]
        
        # Remove any text after the last }
        end_idx = cleaned.rfind('}')
        if end_idx != -1:
            cleaned = cleaned[:end_idx + 1]
        
        # Step 1: Protect existing escape sequences
        escape_map = {
            '\\"': '___ESCAPED_QUOTE___',
            '\\\\': '___ESCAPED_BACKSLASH___',
            '\\n': '___ESCAPED_NEWLINE___',
            '\\r': '___ESCAPED_RETURN___',
            '\\t': '___ESCAPED_TAB___',
            '\\/': '___ESCAPED_SLASH___',
        }
        
        for original, placeholder in escape_map.items():
            cleaned = cleaned.replace(original, placeholder)
        
        # Step 2: Fix common JSON issues
        # 1. Fix trailing commas
        cleaned = re.sub(r',(\s*[}\]])', r'\1', cleaned)
        
        # 2. Fix unquoted keys
        cleaned = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*:)', r'\1"\2"\3', cleaned)
        
        # 3. Fix single quotes to double quotes (but preserve content)
        # First handle single-quoted strings
        def fix_single_quotes(match):
            content = match.group(1)
            # Escape any double quotes in the content
            content = content.replace('"', '\\"')
            return f'"{content}"'
        
        # Replace single-quoted strings with double-quoted ones
        cleaned = re.sub(r"'([^']*)'", fix_single_quotes, cleaned)
        
        # 4. Fix unescaped quotes in string values
        def fix_unescaped_quotes(match):
            prefix = match.group(1)
            content = match.group(2)
            suffix = match.group(3)
            
            # Escape any unescaped quotes in the content
            fixed_content = content.replace('"', '\\"')
            return f'{prefix}"{fixed_content}"{suffix}'
        
        # Apply to string values (not keys)
        cleaned = re.sub(r'(:\s*")([^"]*)"(\s*[,}\]])', fix_unescaped_quotes, cleaned)
        
        # 5. Fix incomplete strings (common issue)
        cleaned = re.sub(r'([^"\\])\.\.\."\s*([,}\]])', r'\1..."\2', cleaned)
        
        # 6. Fix missing quotes around string values (but not numbers/booleans)
        cleaned = re.sub(r':\s*([a-zA-Z][^,}\]]*[^,}\]\s])(\s*[,}\]])', r': "\1"\2', cleaned)
        
        # 7. Fix boolean and null values that might be quoted
        cleaned = re.sub(r':\s*"(true|false|null)"\s*([,}\]])', r': \1\2', cleaned)
        
        # 8. Fix numbers that might be quoted
        cleaned = re.sub(r':\s*"(\d+\.?\d*)"(\s*[,}\]])', r': \1\2', cleaned)
        
        # 9. Handle truncated JSON by adding missing closing braces
        open_braces = cleaned.count('{')
        close_braces = cleaned.count('}')
        if open_braces > close_braces:
            cleaned += '}' * (open_braces - close_braces)
        
        # Step 3: Restore escape sequences
        for original, placeholder in escape_map.items():
            cleaned = cleaned.replace(placeholder, original)
        
        # Try to parse the fixed JSON
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            # If still failing, try one more aggressive fix
            # Remove any incomplete key-value pairs at the end
            lines = cleaned.split('\n')
            for i in range(len(lines) - 1, -1, -1):
                line = lines[i].strip()
                if ':' in line and not line.endswith((',', '}', ']')):
                    lines = lines[:i]
                    break
            
            cleaned = '\n'.join(lines)
            if not cleaned.endswith('}'):
                cleaned += '}'
            
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError:
                # Final fallback to aggressive fix
                return self._aggressive_json_fix(cleaned)
    
    def _extract_json_from_mixed_content(self, response: str) -> Dict[str, Any]:
        """Extract JSON from mixed content with text and JSON"""
        import re
        
        # Look for JSON-like patterns in the text
        json_patterns = [
            r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',  # Nested braces
            r'\{.*?\}',  # Simple braces
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, response, re.DOTALL)
            for match in matches:
                try:
                    return json.loads(match)
                except:
                    continue
        
        raise ValueError("No valid JSON found in mixed content")
    
    def _parse_relaxed_json(self, response: str) -> Dict[str, Any]:
        """Parse JSON with relaxed rules"""
        import re
        
        # Clean the response
        cleaned = response.strip()
        
        # Find the JSON part
        start = cleaned.find('{')
        if start == -1:
            raise ValueError("No JSON object found")
        
        # Find the matching closing brace
        brace_count = 0
        end = start
        for i, char in enumerate(cleaned[start:], start):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    end = i + 1
                    break
        
        json_str = cleaned[start:end]
        
        # Try to fix common issues
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)  # Remove trailing commas
        json_str = re.sub(r'([{,]\s*)(\w+):', r'\1"\2":', json_str)  # Quote unquoted keys
        
        return json.loads(json_str)
    
    def _create_fallback_response(self, original_response: str) -> Dict[str, Any]:
        """Create a fallback response when JSON parsing fails"""
        import re
        
        # Try to extract any useful information from the partial response
        fallback = {
            "error": "json_parsing_failed",
            "original_response": original_response[:500] if original_response else "No response",
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
            "should_revise": True,
            # Additional fields for different response types
            "confidence_assessment": "Low",
            "potential_errors": ["JSON parsing failed"],
            "reasoning_quality_score": 0.1,
            "uncertainty_sources": ["Failed to parse response"],
            "causal_fidelity_score": 0.0,
            "metacognitive_score": 0.1,
            "phenomenal_assessment_score": 0.0,
            "patterns_used": [],
            "scaling_approach": "fallback",
            "approximation_method": "error_handling"
        }
        
        # Try to extract any useful information from the partial response
        if original_response:
            try:
                # Look for confidence or score values in the text
                confidence_matches = re.findall(r'(?:confidence|score)["\']?\s*[:=]\s*([0-9.]+)', original_response, re.IGNORECASE)
                if confidence_matches:
                    confidence_val = float(confidence_matches[0])
                    fallback["confidence"] = min(1.0, max(0.0, confidence_val))
                
                # Try to extract any solution text
                solution_patterns = [
                    r'(?:solution|answer)["\']?\s*[:=]\s*["\']([^"\']+)["\']',
                    r'(?:solution|answer)["\']?\s*[:=]\s*([^,}\]]+)',
                ]
                
                for pattern in solution_patterns:
                    solution_matches = re.findall(pattern, original_response, re.IGNORECASE)
                    if solution_matches:
                        fallback["solution"] = solution_matches[0].strip()
                        break
                
                # Try to extract reasoning steps
                reasoning_patterns = [
                    r'(?:reasoning_steps|steps)["\']?\s*[:=]\s*\[([^\]]+)\]',
                    r'(?:reasoning|steps)["\']?\s*[:=]\s*["\']([^"\']+)["\']',
                ]
                
                for pattern in reasoning_patterns:
                    reasoning_matches = re.findall(pattern, original_response, re.IGNORECASE)
                    if reasoning_matches:
                        fallback["reasoning_steps"] = [reasoning_matches[0].strip()]
                        break
                        
            except Exception as e:
                logger.debug(f"Error extracting information from partial response: {e}")
                pass
            
        return fallback

class MultiLLMValidator:
    """Multi-LLM validation system for cross-verification and consensus building"""
    
    def __init__(self, api_key: Optional[str] = None):
        from config import OPENAI_CONFIG
        self.config = OPENAI_CONFIG
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key required for multi-LLM validation")
        
        # Initialize multiple LLM interfaces
        self.primary_llm = LLMInterface(api_key, self.config["default_model"])
        self.validation_llm = LLMInterface(api_key, self.config["validation_model"])
        self.test_llm = LLMInterface(api_key, self.config["test_model"])
        self.fallback_llm = LLMInterface(api_key, self.config["fallback_model"])
        
        self.validation_enabled = self.config["cross_validation"]["enabled"]
        self.consensus_threshold = self.config["cross_validation"]["consensus_threshold"]
    
    async def validate_reasoning_result(self, problem: str, primary_result: Dict[str, Any],
                                      domain: str = "general") -> Dict[str, Any]:
        """Validate reasoning result using multiple LLMs"""
        if not self.validation_enabled:
            return {"validated": True, "consensus_score": 1.0, "validation_results": []}
        
        validation_prompt = f"""
        Evaluate this reasoning result for correctness and quality:
        
        Problem: {problem}
        Domain: {domain}
        
        Primary Result:
        - Solution: {primary_result.get('solution', 'N/A')}
        - Confidence: {primary_result.get('confidence', 0)}
        - Reasoning: {primary_result.get('reasoning_trace', [])}
        
        Provide your assessment as JSON:
        {{
            "agrees_with_solution": true/false,
            "confidence_in_assessment": 0.0-1.0,
            "alternative_solution": "your solution if different",
            "reasoning_quality": 0.0-1.0,
            "identified_issues": ["list of any issues found"],
            "overall_assessment": "brief assessment"
        }}
        """
        
        validation_results = []
        
        # Get validation from multiple models
        for model_name, llm in [
            ("validation_model", self.validation_llm),
            ("test_model", self.test_llm)
        ]:
            try:
                result = await llm.query_json(validation_prompt)
                result["validator_model"] = model_name
                validation_results.append(result)
            except Exception as e:
                logger.warning(f"Validation failed for {model_name}: {e}")
                validation_results.append({
                    "validator_model": model_name,
                    "error": str(e),
                    "agrees_with_solution": False,
                    "confidence_in_assessment": 0.0
                })
        
        # Calculate consensus
        agreements = [r.get("agrees_with_solution", False) for r in validation_results if "error" not in r]
        consensus_score = sum(agreements) / len(agreements) if agreements else 0.0
        
        return {
            "validated": consensus_score >= self.consensus_threshold,
            "consensus_score": consensus_score,
            "validation_results": validation_results,
            "requires_review": consensus_score < self.consensus_threshold
        }
    
    async def cross_validate_hanoi_20_disk(self, problem: str, primary_result: Dict[str, Any]) -> Dict[str, Any]:
        """Special cross-validation for 20-disk Hanoi problems"""
        
        hanoi_validation_prompt = f"""
        Validate this 20-disk Tower of Hanoi solution:
        
        Problem: {problem}
        Primary Solution: {primary_result.get('solution', 'N/A')}
        
        Check specifically:
        1. Is the mathematical formula 2^20 - 1 = 1,048,575 correct?
        2. Does the solution demonstrate understanding of exponential complexity?
        3. Is the reasoning about recursive structure sound?
        
        Provide validation as JSON:
        {{
            "mathematical_correctness": true/false,
            "formula_verification": "2^20 - 1 = 1048575",
            "complexity_understanding": true/false,
            "recursive_reasoning": true/false,
            "overall_validation": true/false,
            "confidence": 0.0-1.0,
            "notes": "any additional observations"
        }}
        """
        
        validations = []
        
        # Use all available models for 20-disk Hanoi validation
        for model_name, llm in [
            ("validation_model", self.validation_llm),
            ("test_model", self.test_llm),
            ("fallback_model", self.fallback_llm)
        ]:
            try:
                result = await llm.query_json(hanoi_validation_prompt)
                result["validator_model"] = model_name
                validations.append(result)
            except Exception as e:
                logger.warning(f"20-disk Hanoi validation failed for {model_name}: {e}")
        
        # Calculate validation metrics
        math_correct = sum(v.get("mathematical_correctness", False) for v in validations)
        complexity_understood = sum(v.get("complexity_understanding", False) for v in validations)
        recursive_sound = sum(v.get("recursive_reasoning", False) for v in validations)
        overall_valid = sum(v.get("overall_validation", False) for v in validations)
        
        total_validators = len(validations)
        
        return {
            "mathematical_consensus": math_correct / total_validators if total_validators > 0 else 0,
            "complexity_consensus": complexity_understood / total_validators if total_validators > 0 else 0,
            "recursive_consensus": recursive_sound / total_validators if total_validators > 0 else 0,
            "overall_consensus": overall_valid / total_validators if total_validators > 0 else 0,
            "validation_details": validations,
            "high_confidence_validation": (overall_valid / total_validators) >= 0.8 if total_validators > 0 else False
        }
    
    async def consensus_reasoning(self, problem: str, representation_format: str, domain: str) -> Dict[str, Any]:
        """Get consensus reasoning from multiple LLMs"""
        
        reasoning_prompt = f"""
        Solve this problem using systematic reasoning:
        
        Problem: {problem}
        Format: {representation_format}
        Domain: {domain}
        
        Provide your solution as JSON:
        {{
            "solution": "your solution",
            "confidence": 0.0-1.0,
            "reasoning_steps": ["step 1", "step 2", "..."],
            "key_insights": ["insight 1", "insight 2"],
            "certainty_level": "high/medium/low"
        }}
        """
        
        results = []
        
        # Get reasoning from multiple models
        for model_name, llm in [
            ("primary", self.primary_llm),
            ("validation", self.validation_llm),
            ("test", self.test_llm)
        ]:
            try:
                result = await llm.query_json(reasoning_prompt)
                result["source_model"] = model_name
                results.append(result)
            except Exception as e:
                logger.warning(f"Consensus reasoning failed for {model_name}: {e}")
        
        # Analyze consensus
        solutions = [r.get("solution", "") for r in results]
        confidences = [r.get("confidence", 0) for r in results]
        
        # Simple consensus: use highest confidence solution if above threshold
        if confidences:
            best_idx = confidences.index(max(confidences))
            consensus_result = results[best_idx].copy()
            consensus_result["consensus_analysis"] = {
                "total_models": len(results),
                "confidence_range": [min(confidences), max(confidences)],
                "agreement_level": self._calculate_solution_agreement(solutions),
                "all_results": results
            }
            return consensus_result
        
        return {"error": "No valid consensus results", "all_results": results}
    
    def _calculate_solution_agreement(self, solutions: List[str]) -> float:
        """Calculate agreement level between solutions"""
        if len(solutions) < 2:
            return 1.0
        
        # Simple similarity check (can be enhanced with more sophisticated NLP)
        agreements = 0
        total_comparisons = 0
        
        for i in range(len(solutions)):
            for j in range(i + 1, len(solutions)):
                total_comparisons += 1
                # Basic similarity check
                sol1, sol2 = solutions[i].lower(), solutions[j].lower()
                if sol1 and sol2:
                    # Check for key mathematical terms in Hanoi problems
                    if "1048575" in sol1 and "1048575" in sol2:
                        agreements += 1
                    elif "2^20" in sol1 and "2^20" in sol2:
                        agreements += 1
                    elif len(set(sol1.split()) & set(sol2.split())) > len(sol1.split()) * 0.3:
                        agreements += 0.5
        
        return agreements / total_comparisons if total_comparisons > 0 else 0.0


class ReasoningStateMachine:
    """State machine for coordinating reasoning process"""
    
    def __init__(self, llm: LLMInterface):
        self.llm = llm
        self.current_state = ReasoningState.IDLE
        self.state_history: List[ReasoningState] = []
        self.context: Dict[str, Any] = {}
        
    async def transition_to_next_state(self, context: Dict[str, Any]) -> ReasoningState:
        """Subconscious-like state machine - fast, intuitive decisions with loop prevention"""
        
        # CRITICAL: Prevent GENERATING_RESPONSE loops - transition to verification
        if self.current_state == ReasoningState.GENERATING_RESPONSE:
            self.state_history.append(self.current_state)
            self.current_state = ReasoningState.SELF_VERIFICATION
            logger.info(f"Auto-transition to verification: {self.state_history[-1]} -> {self.current_state}")
            return ReasoningState.SELF_VERIFICATION
        
        # Prevent infinite loops by checking state history
        if len(self.state_history) >= 2:
            # If we've been in the same state twice, force completion
            if self.state_history[-1] == self.current_state:
                self.state_history.append(self.current_state)
                self.current_state = ReasoningState.COMPLETE
                logger.info(f"Loop prevention - force complete: {self.state_history[-1]} -> {self.current_state}")
                return ReasoningState.COMPLETE
        
        # Simplified context for subconscious-like processing
        simple_context = {
            "current_state": self.current_state.value,
            "confidence": self._safe_float(context.get('confidence', 0.7)),
            "complexity": self._safe_int(context.get('complexity_level', 3)),
            "has_solution": bool(context.get('fast_solution') or context.get('slow_solution') or context.get('final_solution')),
            "processing_complete": context.get('processing_complete', False)
        }
        
        # Hard-coded transitions for reliability (subconscious-like)
        if self.current_state == ReasoningState.IDLE:
            next_state = ReasoningState.PARSING_INPUT
        elif self.current_state == ReasoningState.PARSING_INPUT:
            next_state = ReasoningState.REPRESENTATION_MAPPING
        elif self.current_state == ReasoningState.REPRESENTATION_MAPPING:
            next_state = ReasoningState.FAST_PROCESSING
        elif self.current_state == ReasoningState.FAST_PROCESSING:
            # If we have a solution with good confidence, skip slow processing
            if simple_context['has_solution'] and simple_context['confidence'] > 0.6:
                next_state = ReasoningState.GENERATING_RESPONSE
            else:
                next_state = ReasoningState.SLOW_PROCESSING
        elif self.current_state == ReasoningState.SLOW_PROCESSING:
            # After slow processing, check if causal analysis is needed
            requires_causal = context.get('requires_causal_analysis', False)
            if requires_causal:
                next_state = ReasoningState.CAUSAL_ANALYSIS
            elif simple_context['complexity'] >= 4:
                next_state = ReasoningState.METACOGNITIVE_EVALUATION
            else:
                next_state = ReasoningState.GENERATING_RESPONSE
        elif self.current_state == ReasoningState.CAUSAL_ANALYSIS:
            # After causal analysis, do metacognitive evaluation for complex problems
            if simple_context['complexity'] >= 4:
                next_state = ReasoningState.METACOGNITIVE_EVALUATION
            else:
                next_state = ReasoningState.GENERATING_RESPONSE
        elif self.current_state == ReasoningState.METACOGNITIVE_EVALUATION:
            next_state = ReasoningState.GENERATING_RESPONSE
        elif self.current_state == ReasoningState.CAUSAL_ANALYSIS:
            next_state = ReasoningState.GENERATING_RESPONSE
        elif self.current_state == ReasoningState.SELF_VERIFICATION:
            next_state = ReasoningState.COMPLETE
        else:
            # Any other state goes to complete
            next_state = ReasoningState.COMPLETE
        
        # Check for error conditions
        if context.get('error_occurred', False) or context.get('parsing_error', False):
            next_state = ReasoningState.ERROR
        
        # Update state
        self.state_history.append(self.current_state)
        self.current_state = next_state
        logger.info(f"Subconscious transition: {self.state_history[-1]} -> {self.current_state}")
        return next_state
    
    def _safe_float(self, value, default=0.0):
        """Safely convert value to float"""
        try:
            return float(value) if value is not None else default
        except (ValueError, TypeError):
            return default
    
    def _safe_int(self, value, default=0):
        """Safely convert value to int"""
        try:
            return int(value) if value is not None else default
        except (ValueError, TypeError):
            return default
    
    def reset(self):
        """Reset state machine"""
        self.current_state = ReasoningState.IDLE
        self.state_history.clear()
        self.context.clear()

class UltraComplexityHandler:
    """Handler for ultra-high complexity problems (20-disk Hanoi level)"""
    
    def __init__(self, llm: LLMInterface):
        self.llm = llm
        self.max_hanoi_discs = 20
        self.max_operations = 2**20 - 1  # 1,048,575 operations
    
    def detect_ultra_complexity(self, problem: str, domain: str) -> Dict[str, Any]:
        """Detect if problem requires ultra-high complexity handling"""
        
        complexity_indicators = [
            "20-disk", "1,048,575", "2^20", "exponential", "ultra-complex",
            "maximum complexity", "theoretical maximum", "hanoi", "tower",
            "hyperdimensional", "multiversal", "quantum", "parallel dimensions"
        ]
        
        problem_lower = problem.lower()
        domain_lower = domain.lower()
        
        # Check for explicit complexity indicators
        has_complexity_indicators = any(indicator in problem_lower or indicator in domain_lower
                                      for indicator in complexity_indicators)
        
        # Estimate operations count from problem description
        estimated_operations = self._estimate_operations_count(problem)
        
        # Check for Hanoi-specific patterns
        hanoi_disc_count = self._extract_hanoi_disc_count(problem)
        
        return {
            'is_ultra_complex': has_complexity_indicators or estimated_operations > 100000 or hanoi_disc_count >= 15,
            'estimated_operations': estimated_operations,
            'hanoi_disc_count': hanoi_disc_count,
            'complexity_level': 5 if has_complexity_indicators else min(5, max(1, int(estimated_operations / 200000) + 1)),
            'requires_exponential_handling': estimated_operations > 50000 or hanoi_disc_count >= 10
        }
    
    def _estimate_operations_count(self, problem: str) -> int:
        """Estimate the number of operations required for the problem"""
        import re
        
        # Look for explicit operation counts
        operation_patterns = [
            r'(\d{1,3}(?:,\d{3})*)\s*operations?',
            r'2\^(\d+)',
            r'(\d+)-disk',
            r'(\d+)\s*parallel\s*dimensions?'
        ]
        
        max_operations = 0
        
        for pattern in operation_patterns:
            matches = re.findall(pattern, problem, re.IGNORECASE)
            for match in matches:
                try:
                    if ',' in str(match):
                        # Handle comma-separated numbers like "1,048,575"
                        num = int(str(match).replace(',', ''))
                    elif 'disk' in pattern:
                        # Handle disk count - convert to operations (2^n - 1)
                        num = 2**int(match) - 1 if int(match) <= 20 else 1048575
                    elif '2^' in pattern:
                        # Handle exponential notation
                        num = 2**int(match) if int(match) <= 20 else 1048575
                    else:
                        num = int(match)
                    
                    max_operations = max(max_operations, num)
                except (ValueError, OverflowError):
                    continue
        
        return max_operations
    
    def _extract_hanoi_disc_count(self, problem: str) -> int:
        """Extract Tower of Hanoi disc count from problem description"""
        import re
        
        hanoi_patterns = [
            r'(\d+)-disk.*hanoi',
            r'hanoi.*(\d+).*disk',
            r'tower.*(\d+).*disk',
            r'(\d+).*disc.*tower'
        ]
        
        for pattern in hanoi_patterns:
            matches = re.findall(pattern, problem, re.IGNORECASE)
            if matches:
                try:
                    return int(matches[0])
                except ValueError:
                    continue
        
        return 0
    
    async def generate_ultra_complex_problem(self, base_problem: str, target_complexity: int = 20) -> str:
        """Generate an ultra-complex version of a problem"""
        
        ultra_prompt = f"""
        Transform this problem into an ultra-high complexity version equivalent to a {target_complexity}-disk Tower of Hanoi problem:
        
        Original Problem: {base_problem}
        Target Complexity: {2**target_complexity - 1:,} operations
        
        Create a version that:
        1. Maintains the logical structure of the original problem
        2. Scales to {target_complexity}-disk Hanoi complexity level
        3. Involves {2**target_complexity - 1:,} parallel operations or dimensions
        4. Uses hyperdimensional or multiversal concepts where appropriate
        5. Preserves the core reasoning requirements
        
        Return the ultra-complex problem statement.
        """
        
        try:
            response = await self.llm.query(ultra_prompt,
                "You are an expert at scaling problems to ultra-high complexity while preserving logical structure.")
            return response.strip()
        except Exception as e:
            # Fallback: create a basic ultra-complex version
            return f"Across {2**target_complexity - 1:,} parallel logical dimensions, {base_problem}"

class T1ReasoningEngine:
    """T1: Reasoning-Capability Tautology Implementation"""
    
    def __init__(self, llm: LLMInterface):
        self.llm = llm
        self.state_machine = ReasoningStateMachine(llm)
        self.ultra_complexity_handler = UltraComplexityHandler(llm)  # New: Ultra-complexity support
    
    def _safe_float(self, value, default=0.0):
        """Safely convert value to float"""
        try:
            return float(value) if value is not None else default
        except (ValueError, TypeError):
            return default
    
    def _safe_int(self, value, default=0):
        """Safely convert value to int"""
        try:
            return int(value) if value is not None else default
        except (ValueError, TypeError):
            return default
    
    async def reason(self, context: ReasoningContext) -> ReasoningResult:
        """Main reasoning method implementing T1 tautology with ultra-complexity support"""
        start_time = time.time()
        reasoning_trace = []
        state_transitions = []
        
        # Detect and handle ultra-complexity
        ultra_analysis = self.ultra_complexity_handler.detect_ultra_complexity(
            context.problem, context.domain
        )
        
        # Update context with ultra-complexity information
        if ultra_analysis['is_ultra_complex']:
            context.is_ultra_complex = True
            context.complexity_level = max(context.complexity_level, ultra_analysis['complexity_level'])
            context.hanoi_disc_count = ultra_analysis['hanoi_disc_count']
            context.exponential_operations = ultra_analysis['estimated_operations']
            reasoning_trace.append(f"Ultra-complexity detected: {ultra_analysis['estimated_operations']:,} operations")
        
        # Reset state machine
        self.state_machine.reset()
        
        # Initialize enhanced context
        sm_context = {
            'problem': context.problem,
            'representation_format': context.representation_format,
            'domain': context.domain,
            'complexity_level': context.complexity_level,
            'requires_causal_analysis': context.requires_causal_analysis,
            'requires_metacognition': context.requires_metacognition,
            'uncertainty_threshold': context.uncertainty_threshold,
            'is_ultra_complex': context.is_ultra_complex,
            'hanoi_disc_count': context.hanoi_disc_count,
            'exponential_operations': context.exponential_operations,
            'fast_slow_switching_enabled': context.fast_slow_switching_enabled,
            'ultra_analysis': ultra_analysis
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
            
            elif current_state == ReasoningState.ERROR:
                # Handle error state - log error and prepare error response
                error_msg = sm_context.get('error_message', 'Unknown error occurred')
                reasoning_trace.append(f"ERROR: {error_msg}")
                logger.error(f"Reasoning failed: {error_msg}")
                sm_context['final_solution'] = f"Error: {error_msg}"
                sm_context['confidence'] = 0.0
                break  # Exit the processing loop
            
            # Transition to next state
            await self.state_machine.transition_to_next_state(sm_context)
        
        # Check T1 compliance
        t1_compliance = await self._check_t1_compliance(sm_context, context)
        
        end_time = time.time()
        
        return ReasoningResult(
            success=True,
            solution=sm_context.get('final_solution', 'No solution generated'),
            confidence=self._safe_float(sm_context.get('confidence', 0.0)),
            reasoning_trace=reasoning_trace,
            state_transitions=[{'state': s, 'timestamp': time.time()} for s in state_transitions],
            processing_time=end_time - start_time,
            internal_state=sm_context.get('internal_representation', {}),
            mode_used=ReasoningMode.SLOW_DELIBERATIVE,
            time_taken=end_time - start_time,
            uncertainty_estimate=1.0 - self._safe_float(sm_context.get('confidence', 0.0)),
            causal_graph=sm_context.get('causal_graph'),
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
        
        # Safely serialize parsed input
        try:
            parsed_input_json = json.dumps(context.get('parsed_input', {}), indent=2)
        except (TypeError, ValueError) as e:
            parsed_input_json = f"Serialization error: {str(e)}"
        
        mapping_prompt = f"""
        Create an internal representation from the parsed input that preserves logical structure
        across different surface representations.
        
        Parsed Input: {parsed_input_json}
        
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
        """Enhanced fast, intuitive processing with ultra-complexity awareness"""
        
        # Check if ultra-complex problem requires different approach
        is_ultra_complex = context.get('is_ultra_complex', False)
        exponential_operations = context.get('exponential_operations', 0)
        
        # Safely serialize internal representation
        try:
            internal_rep_json = json.dumps(context.get('internal_representation', {}), indent=2)
        except (TypeError, ValueError) as e:
            internal_rep_json = f"Serialization error: {str(e)}"
        
        if is_ultra_complex:
            fast_prompt = f"""
            Perform ULTRA-COMPLEX FAST REASONING for {exponential_operations:,} operation problem:
            
            Internal Representation: {internal_rep_json}
            Problem: {context.get('problem', '')}
            Complexity Level: Ultra-High ({exponential_operations:,} operations)
            
            ULTRA-COMPLEX FAST STRATEGY:
            1. EXPONENTIAL PATTERN RECOGNITION:
            - Identify if this is a 20-disk Hanoi equivalent problem
            - Look for exponential growth patterns (2^n relationships)
            - Recognize hyperdimensional or multiversal structures
            - Apply ultra-high complexity heuristics
            
            2. SCALING PATTERN DETECTION:
            - Detect if problem scales exponentially vs polynomially
            - Identify recursive substructures that repeat at scale
            - Look for parallel processing opportunities
            - Apply divide-and-conquer at massive scale
            
            3. ULTRA-COMPLEXITY HEURISTICS:
            - Use approximation methods for intractable exact solutions
            - Apply probabilistic reasoning for massive state spaces
            - Leverage symmetry and invariance properties
            - Consider quantum-inspired parallel processing
            
            ULTRA-COMPLEX CONFIDENCE CALIBRATION:
            - High confidence (0.7-1.0): Clear exponential pattern, proven scaling method
            - Medium confidence (0.4-0.6): Partial pattern match, scaling uncertainty
            - Low confidence (0.0-0.3): Novel ultra-complex pattern, heuristics uncertain
            
            CRITICAL: For ultra-complex problems, even "fast" reasoning must acknowledge the
            exponential nature and provide approximation strategies rather than exact solutions.
            
            Return JSON with: solution, confidence (0-1), reasoning_steps, patterns_used,
            scaling_approach, approximation_method.
            """
        else:
            fast_prompt = f"""
            Perform fast, intuitive reasoning using SPECIFIC PATTERN RECOGNITION CRITERIA:
            
            Internal Representation: {internal_rep_json}
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
        and heuristics to quickly solve problems. Don't overthink - go with your first instinct.
        
        CRITICAL: Your goal is to FIND THE SOLUTION, not to give algorithms or implementations.
        Focus on what the answer IS, not how to compute it. Give the final result or conclusion."""
        
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
        
        # Safely serialize internal representation
        try:
            internal_rep_json = json.dumps(context.get('internal_representation', {}), indent=2)
        except (TypeError, ValueError) as e:
            internal_rep_json = f"Serialization error: {str(e)}"
        
        slow_prompt = f"""
        Perform careful, deliberative reasoning using SYSTEMATIC LOGICAL ANALYSIS:
        
        Internal Representation: {internal_rep_json}
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
        Apply formal logic, check your work, consider alternatives. Be thorough and precise.
        
        CRITICAL: Your goal is to FIND THE SOLUTION, not to give algorithms or implementations.
        Focus on what the answer IS, not how to compute it. Give the final result or conclusion."""
        
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
        """Enhanced causal analysis with do-calculus and structural fidelity"""
        
        # Safely serialize internal representation
        try:
            internal_rep_json = json.dumps(context.get('internal_representation', {}), indent=2)
        except (TypeError, ValueError) as e:
            internal_rep_json = f"Serialization error: {str(e)}"
        
        is_ultra_complex = context.get('is_ultra_complex', False)
        
        if is_ultra_complex:
            causal_prompt = f"""
            Perform ULTRA-COMPLEX CAUSAL ANALYSIS with do-calculus for {context.get('exponential_operations', 0):,} operation problem:
            
            Problem: {context.get('problem', '')}
            Internal Representation: {internal_rep_json}
            Complexity: Ultra-High (20-disk Hanoi equivalent)
            
            ADVANCED CAUSAL STRUCTURAL FIDELITY ANALYSIS:
            
            1. HYPERDIMENSIONAL CAUSAL GRAPH CONSTRUCTION:
            - Identify causal variables across {context.get('exponential_operations', 0):,} parallel dimensions
            - Map causal relationships that scale exponentially
            - Build multi-level causal hierarchies
            - Account for quantum superposition of causal states
            
            2. DO-CALCULUS INTERVENTIONS AT SCALE:
            - Define intervention operators do(X) for massive variable sets
            - Calculate P(Y|do(X)) for exponentially large outcome spaces
            - Consider intervention effects across parallel causal chains
            - Model cascading interventions through hyperdimensional structures
            
            3. STRUCTURAL CAUSAL MODEL (SCM) FIDELITY:
            - Verify causal graph mirrors true domain structure at ultra-scale
            - Test causal assumptions across exponential state spaces
            - Validate structural equations for massive variable interactions
            - Ensure causal fidelity maintains across dimensional scaling
            
            4. COUNTERFACTUAL REASONING AT ULTRA-COMPLEXITY:
            - Generate counterfactuals: "What if we intervened on 2^n variables simultaneously?"
            - Analyze nearest possible worlds across exponential possibility spaces
            - Consider counterfactual stability across dimensional boundaries
            - Model butterfly effects in hyperdimensional causal networks
            
            Return JSON with: causal_variables, causal_relationships, causal_graph,
            do_calculus_interventions, structural_equations, counterfactual_scenarios,
            causal_fidelity_score, ultra_complexity_adaptations.
            """
        else:
            causal_prompt = f"""
            Perform ENHANCED CAUSAL ANALYSIS with do-calculus and structural fidelity:
            
            Problem: {context.get('problem', '')}
            Internal Representation: {internal_rep_json}
            
            CAUSAL STRUCTURAL FIDELITY ANALYSIS:
            
            1. CAUSAL GRAPH CONSTRUCTION:
            - Identify all causal variables in the domain
            - Determine causal relationships (X → Y, X ← Y, X ↔ Y)
            - Build directed acyclic graph (DAG) representing causal structure
            - Identify confounders, mediators, and colliders
            
            2. DO-CALCULUS INTERVENTIONS:
            - Define intervention operators do(X) for key variables
            - Calculate P(Y|do(X)) - probability of Y given intervention on X
            - Distinguish causation from correlation using intervention logic
            - Model what happens when we "break" causal arrows through intervention
            
            3. STRUCTURAL CAUSAL MODEL (SCM):
            - Define structural equations for each variable
            - Specify noise terms and their distributions
            - Ensure model captures true causal mechanisms of the domain
            - Validate that internal representation mirrors real causal structure
            
            4. COUNTERFACTUAL REASONING:
            - Generate counterfactuals: "What would have happened if X had been different?"
            - Use three-step process: abduction, action, prediction
            - Analyze nearest possible worlds and counterfactual stability
            - Test causal claims through counterfactual implications
            
            Return JSON with: causal_variables, causal_relationships, causal_graph,
            do_calculus_interventions, structural_equations, counterfactual_scenarios,
            causal_fidelity_score, validation_tests.
            """
        
        system_prompt = """You are performing causal analysis. Focus on identifying true causal
        relationships, not just correlations. Consider what would happen under interventions.
        
        CRITICAL: Your goal is to FIND THE SOLUTION, not to give algorithms or implementations.
        Focus on what the causal relationships ARE, not how to compute them. Give the final analysis."""
        
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
        Evaluate compliance with T1 Reasoning-Capability Tautology using REALISTIC CRITERIA:

        REQUIREMENT R1 - Correct Solution from Any Representation:
        - PASS if: Solution is logically correct, demonstrates valid reasoning steps, addresses the actual problem, confidence ≥0.8
        - FAIL if: Solution is incorrect, illogical, contradictory, or fails to address the problem
        - Current confidence: {context.get('confidence', 0)}
        - CRITICAL: For 13th order logic, solution must correctly interpret the logical structure, not dismiss as "contradictory"
        - ANALYSIS: Is the solution actually correct and does it demonstrate proper logical reasoning?

        REQUIREMENT R2 - Success Under Distribution Shift:
        - PASS if: Solution quality maintained across formats, shows format adaptability, confidence ≥0.8
        - FAIL if: Performance degrades significantly with format changes or unusual domains
        - Format adaptability required for: {original_context.representation_format}
        - ANALYSIS: Does the system maintain reasoning quality across different representation formats?

        COROLLARY C1 - Representation Invariance:
        - PASS if: Solution quality consistent across formats, recognizes core logical structure, confidence ≥0.8
        - FAIL if: Cannot handle different formats or misinterprets logical structure due to format
        - CRITICAL: Must demonstrate format-independent logical reasoning, not format-dependent failures
        - ANALYSIS: Does the system maintain logical accuracy regardless of representation format?

        COROLLARY C2 - Complexity Scaling:
        - PASS if: Handles complex problems systematically, maintains logical rigor, confidence ≥0.8
        - FAIL if: Fails to engage with complexity or provides oversimplified/incorrect solutions
        - Problem complexity level: {original_context.complexity_level}
        - CRITICAL: For ultra-complex problems (13th order logic), must engage with the complexity, not dismiss it
        - ANALYSIS: Does the system scale reasoning capabilities appropriately with problem complexity?

        COROLLARY C3 - Zero-Shot Robustness:
        - PASS if: Handles novel patterns with logical rigor, maintains reasoning quality, confidence ≥0.8
        - FAIL if: Fails on novel patterns or provides poor quality reasoning
        - CRITICAL: Must demonstrate robust reasoning on unfamiliar logical structures
        - ANALYSIS: Does the system maintain reasoning quality on novel problem types?

        PROBLEM ANALYSIS:
        Problem: {original_context.problem}
        Format: {original_context.representation_format}
        Solution: {context.get('final_solution', '')}
        Confidence: {context.get('confidence', 0)}
        
        EVALUATION INSTRUCTIONS:
        1. Be RIGOROUS in evaluation - high standards are required for tautology compliance
        2. PASS only if the system demonstrates correct, logical, and coherent reasoning
        3. FAIL if solution is incorrect, contradictory, dismissive, or shows poor reasoning quality
        4. Confidence scores below 0.5 indicate insufficient reasoning quality for PASS
        5. For complex formats (13th order logic), dismissing as "contradictory" without proper analysis is FAIL
        6. Focus on actual correctness and reasoning quality, not just effort or attempt
        7. CRITICAL: "Unsatisfiable" or "contradictory" responses to valid logical problems indicate FAIL
        
        Return JSON with: r1_compliance, r2_compliance, c1_compliance, c2_compliance,
        c3_compliance, overall_t1_compliance, compliance_score (0-1).
        """
        
        system_prompt = """Evaluate compliance with the T1 Reasoning-Capability Tautology.
        Be objective in assessing whether the reasoning meets the formal requirements.
        
        CRITICAL: Focus on whether the system FOUND A SOLUTION, not whether it gave algorithms.
        Evaluate based on the quality of the final answer and reasoning, not implementation details."""
        
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
        
        # Safely serialize internal representation
        try:
            internal_rep_json = json.dumps(internal_rep, indent=2)
        except (TypeError, ValueError) as e:
            internal_rep_json = f"Serialization error: {str(e)}"
        
        truth_prompt = f"""
        Extract the truth value from this internal representation:
        
        Internal Representation: {internal_rep_json}
        
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
                return float(score) if score is not None else 0.7
            except (ValueError, TypeError):
                return 0.7  # Default fallback
        except Exception as e:
            trace.append(f"Modal invariance test failed: {str(e)}")
            return 0.0
    
    async def _test_counterfactual_competence(self, internal_rep: Dict[str, Any], trace: List[str]) -> float:
        """Test C5: Counterfactual competence"""
        
        # Safely serialize internal representation
        try:
            internal_rep_json = json.dumps(internal_rep, indent=2)
        except (TypeError, ValueError) as e:
            internal_rep_json = f"Serialization error: {str(e)}"
        
        counterfactual_prompt = f"""
        Test counterfactual competence using this internal representation:
        
        Internal Representation: {internal_rep_json}
        
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
                return float(score) if score is not None else 0.7
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
                return float(score) if score is not None else 0.7
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
        - PASS if: Understanding survives cross-modal transfer, modal score ≥0.7, demonstrates format independence
        - FAIL if: Understanding degrades across modalities or shows format dependency
        - Current modal invariance score: {modal_score}
        - CRITICAL: Must maintain understanding quality across different representation modalities

        COROLLARY C5 - Counterfactual Competence:
        - PASS if: Correctly reasons about counterfactuals, generates valid inferences, counterfactual score ≥0.6
        - FAIL if: Cannot reason about counterfactuals, provides incorrect inferences, or shows logical errors
        - Current counterfactual competence score: {counterfactual_score}
        - CRITICAL: Must demonstrate logical rigor in counterfactual reasoning

        COROLLARY C6 - Distribution Shift Robustness:
        - PASS if: Maintains truth evaluation accuracy with novel examples, distribution score ≥0.6
        - FAIL if: Performance degrades significantly with distribution shift or novel examples
        - Current distribution robustness score: {distribution_score}
        - CRITICAL: Must show robust understanding across different example distributions

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
        Assess whether the understanding meets the formal requirements.
        
        CRITICAL: Focus on whether the system FOUND THE UNDERSTANDING, not whether it gave algorithms.
        Evaluate based on the quality of comprehension and analysis, not implementation details."""
        
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
            phenomenal_awareness=phenomenal_assessment,
            deep_understanding_score=deep_score,
            extended_understanding_trace=extended_trace,
            tautology_compliance=tustar_compliance
        )
    
    async def _assess_causal_structural_fidelity(self, proposition: str, domain: str,
                                               internal_rep: Dict[str, Any], trace: List[str]) -> Dict[str, Any]:
        """E1: Assess causal structural fidelity"""
        
        # Safely serialize internal representation
        try:
            internal_rep_json = json.dumps(internal_rep, indent=2)
        except (TypeError, ValueError) as e:
            internal_rep_json = f"Serialization error: {str(e)}"
        
        causal_prompt = f"""
        Assess causal structural fidelity for deep understanding:
        
        Proposition: {proposition}
        Domain: {domain}
        Internal Representation: {internal_rep_json}
        
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
        
        # Safely serialize the base understanding data
        try:
            base_understanding_json = json.dumps(base_understanding.__dict__, indent=2, default=str)
        except (TypeError, ValueError) as e:
            base_understanding_json = f"Serialization error: {str(e)}"
        
        metacognitive_prompt = f"""
        Analyze the metacognitive capabilities demonstrated in this reasoning process:
        
        Base Understanding: {base_understanding_json}
        
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
        
        # Safely serialize the base understanding data
        try:
            base_understanding_json = json.dumps(base_understanding.__dict__, indent=2, default=str)
        except (TypeError, ValueError) as e:
            base_understanding_json = f"Serialization error: {str(e)}"
        
        phenomenal_prompt = f"""
        Conduct a theoretical analysis of consciousness-related indicators in AI reasoning:
        
        Base Understanding: {base_understanding_json}
        
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
        - PASS if: Demonstrates sophisticated causal reasoning, correctly identifies causal relationships, causal fidelity score ≥0.5
        - FAIL if: Cannot distinguish causation from correlation, poor causal analysis, or incorrect causal inferences
        - Current causal fidelity score: {causal_fidelity.get('causal_fidelity_score', 0)}
        - CRITICAL: Must show deep understanding of causal mechanisms, not superficial pattern matching

        EXTENDED REQUIREMENT E2 - Metacognitive Self-Awareness:
        - PASS if: Demonstrates genuine self-awareness of reasoning process, accurate self-assessment, metacognitive score ≥0.5
        - FAIL if: No metacognitive insight, inaccurate self-assessment, or lacks awareness of reasoning limitations
        - Current metacognitive score: {metacognitive_awareness.get('metacognitive_score', 0)}
        - CRITICAL: Must show authentic metacognitive capabilities, not just reporting confidence scores

        EXTENDED REQUIREMENT E3 - Phenomenal Awareness (Theoretical):
        - PASS if: Shows indicators of subjective experience awareness, recognizes qualitative aspects, phenomenal score ≥0.5
        - FAIL if: Purely mechanical responses, no recognition of experiential/subjective dimensions
        - Current phenomenal score: {phenomenal_assessment.get('phenomenal_assessment_score', 0)}
        - CRITICAL: While theoretical, must demonstrate some awareness of subjective/experiential aspects

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
        Consider both the base TU requirements and the extended E1, E2, E3 requirements.
        
        CRITICAL: Focus on whether the system ACHIEVED DEEP UNDERSTANDING, not whether it gave algorithms.
        Evaluate based on the quality of insight and comprehension, not implementation details."""
        
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

class FastSlowThinkingCoordinator:
    """Coordinator for dynamic fast/slow thinking integration as described in Bhatt Conjectures"""
    
    def __init__(self, llm: LLMInterface):
        self.llm = llm
        self.fast_threshold = 0.8  # Confidence threshold for fast-only processing
        self.slow_threshold = 0.6  # Confidence threshold below which slow processing is required
        self.uncertainty_threshold = 0.7  # Uncertainty threshold for mode switching
    
    def should_switch_to_slow(self, fast_result: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Determine if we should switch from fast to slow thinking"""
        
        fast_confidence = fast_result.get('confidence', 0.0)
        is_ultra_complex = context.get('is_ultra_complex', False)
        complexity_level = context.get('complexity_level', 3)
        
        # Always use slow thinking for ultra-complex problems
        if is_ultra_complex:
            return True
        
        # Switch to slow if confidence is below threshold
        if fast_confidence < self.slow_threshold:
            return True
        
        # Switch to slow for high complexity problems regardless of confidence
        if complexity_level >= 4:
            return True
        
        # Check for uncertainty indicators in fast reasoning
        patterns_used = fast_result.get('patterns_used', [])
        if not patterns_used or 'uncertain' in str(patterns_used).lower():
            return True
        
        return False
    
    def should_use_metacognitive_evaluation(self, context: Dict[str, Any],
                                          fast_result: Dict[str, Any],
                                          slow_result: Dict[str, Any] = None) -> bool:
        """Determine if metacognitive evaluation is needed"""
        
        is_ultra_complex = context.get('is_ultra_complex', False)
        complexity_level = context.get('complexity_level', 3)
        
        # Always use metacognitive evaluation for ultra-complex problems
        if is_ultra_complex:
            return True
        
        # Use for high complexity problems
        if complexity_level >= 4:
            return True
        
        # Use if there's disagreement between fast and slow thinking
        if slow_result:
            fast_conf = fast_result.get('confidence', 0.0)
            slow_conf = slow_result.get('confidence', 0.0)
            if abs(fast_conf - slow_conf) > 0.3:
                return True
        
        # Use if confidence is in uncertain range
        current_confidence = slow_result.get('confidence', 0.0) if slow_result else fast_result.get('confidence', 0.0)
        if 0.4 <= current_confidence <= 0.7:
            return True
        
        return False
    
    async def coordinate_thinking_modes(self, context: Dict[str, Any],
                                      fast_result: Dict[str, Any],
                                      trace: List[str]) -> Dict[str, Any]:
        """Coordinate between fast and slow thinking modes"""
        
        coordination_result = {
            'mode_used': 'fast_only',
            'final_solution': fast_result.get('solution', ''),
            'final_confidence': fast_result.get('confidence', 0.0),
            'reasoning_trace': fast_result.get('reasoning_steps', []),
            'coordination_notes': []
        }
        
        # Check if we need slow thinking
        if self.should_switch_to_slow(fast_result, context):
            coordination_result['mode_used'] = 'hybrid_fast_slow'
            coordination_result['coordination_notes'].append("Switched to slow thinking due to uncertainty/complexity")
            trace.append("Fast/Slow Coordinator: Switching to slow thinking")
            
            # Note: Slow thinking would be handled by the main reasoning engine
            # This coordinator just makes the decision
        
        # Check for mode switching recommendations
        fast_confidence = fast_result.get('confidence', 0.0)
        if fast_confidence > self.fast_threshold:
            coordination_result['coordination_notes'].append("High confidence - fast thinking sufficient")
        elif fast_confidence < self.slow_threshold:
            coordination_result['coordination_notes'].append("Low confidence - slow thinking recommended")
        else:
            coordination_result['coordination_notes'].append("Medium confidence - hybrid approach optimal")
        
        return coordination_result

class AgenticReasoningSystemSDK:
    """Main SDK class implementing the complete Bhatt Conjectures framework"""
    
    def __init__(self, openai_api_key: Optional[str] = None, model: str = "o3", enable_multi_llm_validation: bool = True):
        """Initialize the Agentic Reasoning System SDK with multi-LLM validation"""
        self.llm = LLMInterface(openai_api_key, model)
        self.t1_engine = T1ReasoningEngine(self.llm)
        self.tu_engine = TUUnderstandingEngine(self.llm)
        self.tustar_engine = TUStarExtendedUnderstandingEngine(self.llm, self.tu_engine)
        self.fast_slow_coordinator = FastSlowThinkingCoordinator(self.llm)
        
        # Initialize multi-LLM validation system
        self.enable_validation = enable_multi_llm_validation
        if self.enable_validation:
            try:
                self.multi_llm_validator = MultiLLMValidator(openai_api_key)
                logger.info("Multi-LLM validation system initialized")
            except Exception as e:
                logger.warning(f"Multi-LLM validation disabled due to error: {e}")
                self.multi_llm_validator = None
                self.enable_validation = False
        else:
            self.multi_llm_validator = None
        
        logger.info("Agentic Reasoning System SDK initialized with enhanced fast/slow thinking and multi-LLM validation")
    
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
        
        # Get primary reasoning result
        result = await self.t1_engine.reason(context)
        
        # Apply multi-LLM validation for high-complexity problems
        if self.enable_validation and self.multi_llm_validator:
            # Special validation for 20-disk Hanoi problems
            if "20" in problem and ("hanoi" in problem.lower() or "tower" in problem.lower()):
                validation = await self.multi_llm_validator.cross_validate_hanoi_20_disk(
                    problem, {
                        "solution": result.solution,
                        "confidence": result.confidence,
                        "reasoning_trace": result.reasoning_trace
                    }
                )
                result.validation_results = validation
                
                # Adjust confidence based on validation consensus
                if validation.get("high_confidence_validation", False):
                    result.confidence = min(1.0, result.confidence * 1.1)  # Boost confidence
                elif validation.get("overall_consensus", 0) < 0.5:
                    result.confidence = max(0.1, result.confidence * 0.8)  # Reduce confidence
            
            # General validation for complex problems
            elif complexity_level >= 4:
                validation = await self.multi_llm_validator.validate_reasoning_result(
                    problem, {
                        "solution": result.solution,
                        "confidence": result.confidence,
                        "reasoning_trace": result.reasoning_trace
                    }, domain
                )
                result.validation_results = validation
                
                # Adjust confidence based on validation
                if validation.get("validated", False):
                    result.confidence = min(1.0, result.confidence * 1.05)
                elif validation.get("requires_review", False):
                    result.confidence = max(0.1, result.confidence * 0.9)
        
        return result
    
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
                'phenomenal_assessment': tustar_result.phenomenal_awareness
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