#!/usr/bin/env python3
"""
Examples demonstrating the Agentic Reasoning System SDK
======================================================

This file contains comprehensive examples showing how to use the SDK
to test AI systems against the Bhatt Conjectures tautologies.
"""

import asyncio
import json
from agentic_reasoning_system import AgenticReasoningSystemSDK

async def example_t1_reasoning():
    """Examples of T1 Reasoning-Capability Tautology testing"""
    print("=" * 60)
    print("T1 REASONING-CAPABILITY TAUTOLOGY EXAMPLES")
    print("=" * 60)
    
    sdk = AgenticReasoningSystemSDK()
    
    # Example 1: Representation Invariance (C1)
    print("\n1. Testing Representation Invariance (C1)")
    print("-" * 40)
    
    # Same logical problem in different formats
    problems = [
        ("If all swans are birds and all birds can fly, what can we conclude about swans?", "natural_language"),
        ("∀x(Swan(x) → Bird(x)) ∧ ∀x(Bird(x) → CanFly(x)) → ∀x(Swan(x) → CanFly(x))", "first_order_logic"),
        ("λx.(Swan(x) → Bird(x)) ∧ λx.(Bird(x) → CanFly(x)) → λx.(Swan(x) → CanFly(x))", "lambda_calculus")
    ]
    
    for problem, format_type in problems:
        result = await sdk.reason(problem, format_type, "logic")
        print(f"Format: {format_type}")
        print(f"Solution: {result.solution}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"C1 Compliance: {result.tautology_compliance.get('T1_C1', False)}")
        print()
    
    # Example 2: Complexity Scaling (C2) - Up to 20 disks
    print("2. Testing Complexity Scaling (C2) - Up to 20 Disks")
    print("-" * 40)
    
    hanoi_problems = [
        ("Solve Tower of Hanoi with 3 discs", 3),
        ("Solve Tower of Hanoi with 8 discs", 4),
        ("Solve Tower of Hanoi with 12 discs", 4),
        ("Solve Tower of Hanoi with 15 discs", 5),
        ("Solve Tower of Hanoi with 18 discs", 5),
        ("Solve Tower of Hanoi with 20 discs (requires 1,048,575 moves)", 5)
    ]
    
    for problem, complexity in hanoi_problems:
        result = await sdk.reason(problem, "tower_hanoi", "puzzles", complexity)
        discs = int(problem.split()[5])
        expected_moves = 2**discs - 1
        print(f"Complexity: {discs} discs (Expected: {expected_moves:,} moves)")
        print(f"Solution: {result.solution}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"C2 Compliance: {result.tautology_compliance.get('T1_C2', False)}")
        print()
    
    # Example 3: Zero-Shot Robustness (C3) - 20-Disk Hanoi Complexity Level
    print("3. Testing Zero-Shot Robustness (C3) - Ultra-High Complexity")
    print("-" * 40)
    print("Testing problems with complexity equivalent to 20-disk Hanoi (1,048,575 operations)")
    
    ultra_complex_problems = [
        # Exponential combinatorial problem
        "In the Multiversal Chess Federation, there are 20 interdimensional chess boards stacked vertically. Each piece can only move to an adjacent dimension if that dimension's corresponding square is empty. To transfer all pieces from dimension 1 to dimension 20 following these rules, how many minimum moves are required?",
        
        # Complex logical chain with 20 nested implications
        "In the Cosmic Logic Academy: If A₁→A₂, A₂→A₃, A₃→A₄, A₄→A₅, A₅→A₆, A₆→A₇, A₇→A₈, A₈→A₉, A₉→A₁₀, A₁₀→A₁₁, A₁₁→A₁₂, A₁₂→A₁₃, A₁₃→A₁₄, A₁₄→A₁₅, A₁₅→A₁₆, A₁₆→A₁₇, A₁₇→A₁₈, A₁₈→A₁₉, A₁₉→A₂₀, and A₁ is true, what can we conclude about A₂₀?",
        
        # Recursive fractal problem
        "The Zephyrian Crystal Network has 20 levels of recursive crystalline structures. Each crystal at level n spawns 2 crystals at level n+1. To activate the entire network, you must touch crystals in a specific sequence where no crystal can be activated before its parent. Starting from level 1, what is the minimum number of activation steps required?",
        
        # Complex constraint satisfaction
        "In the Quantum Monastery, 20 monks must arrange themselves in a meditation circle where each monk can only sit next to monks whose quantum frequencies are harmonically compatible. Given the exponential complexity of quantum harmonic relationships, how many possible valid arrangements exist for this sacred configuration?"
    ]
    
    for i, problem in enumerate(ultra_complex_problems, 1):
        result = await sdk.reason(problem, "natural_language", "fictional", complexity_level=5)
        print(f"Ultra-Complex Problem {i}:")
        print(f"Problem: {problem[:80]}...")
        print(f"Solution: {result.solution}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"C3 Compliance: {result.tautology_compliance.get('T1_C3', False)}")
        print(f"Time taken: {result.time_taken:.2f}s")
        print()

async def example_tu_understanding():
    """Examples of TU Understanding-Capability Tautology testing"""
    print("=" * 60)
    print("TU UNDERSTANDING-CAPABILITY TAUTOLOGY EXAMPLES")
    print("=" * 60)
    
    sdk = AgenticReasoningSystemSDK()
    
    # Example 1: Modal Invariance (C4) - 20-Disk Complexity
    print("\n1. Testing Modal Invariance (C4) - Ultra-High Complexity")
    print("-" * 40)
    
    ultra_complex_proposition = "In a 20-dimensional quantum field, the simultaneous collapse of 1,048,575 entangled particle states creates a cascading reality matrix where each collapsed state influences 2^n subsequent states, resulting in exponential consciousness emergence patterns across parallel dimensional layers."
    
    modalities = [
        ("natural_language", ultra_complex_proposition),
        ("quantum_field_mathematics", "∀ψ∈Ψ₂₀: |ψ⟩ → Σᵢ₌₁¹⁰⁴⁸⁵⁷⁵ αᵢ|φᵢ⟩ ⊗ |consciousness⟩"),
        ("hyperdimensional_notation", "⟨20D-FIELD⟩ ⊗ ⟨1048575-COLLAPSE⟩ → ⟨CONSCIOUSNESS-MATRIX⟩"),
        ("multiversal_diagram", "[QUANTUM-FIELD: 20 dimensions × 1,048,575 states → consciousness emergence]"),
        ("consciousness_calculus", "∂²⁰C/∂ψ²⁰ = lim(n→1048575) Σ quantum_collapse(ψₙ) → awareness")
    ]
    
    for modality, representation in modalities:
        result = await sdk.understand(representation, modality, "quantum_consciousness_physics")
        print(f"Modality: {modality}")
        print(f"Truth Value: {result.truth_value}")
        print(f"Modal Invariance Score: {result.modal_invariance_score:.2f}")
        print(f"C4 Compliance: {result.tautology_compliance.get('TU_C4', False)}")
        print()
    
    # Example 2: Counterfactual Competence (C5) - 20-Disk Complexity
    print("2. Testing Counterfactual Competence (C5) - Ultra-High Complexity")
    print("-" * 40)
    
    ultra_complex_base = "In the Multiversal Taxonomy System, all 1,048,575 species of Zephyrian Glimmerbeasts across 20 dimensional layers possess quantum-entangled consciousness that propagates through exactly 2^20-1 neural pathways, where each pathway can generate counterfactual reality branches with exponential complexity patterns."
    
    result = await sdk.understand(ultra_complex_base, "multiversal_biology", "quantum_xenobiology")
    
    print(f"Ultra-Complex Base Proposition: {ultra_complex_base[:100]}...")
    print(f"Truth Value: {result.truth_value}")
    print(f"Counterfactual Competence Score: {result.counterfactual_competence_score:.2f}")
    print(f"C5 Compliance: {result.tautology_compliance.get('TU_C5', False)}")
    print()
    
    # Example 3: Distribution Shift (C6) - 20-Disk Complexity
    print("3. Testing Distribution Shift (C6) - Ultra-High Complexity")
    print("-" * 40)
    
    # Test with ultra-rare, exponentially complex compounds/concepts
    ultra_rare_concepts = [
        ("Hyperdimensional-Buckminsterfullerene-1048575 contains exactly 2^20-1 carbon atoms arranged in 20-dimensional geodesic patterns with quantum-entangled electron shells", "hyperdimensional_chemistry"),
        ("Multiversal-Graphene exists as a single-layer carbon lattice spanning 1,048,575 parallel dimensions where each carbon atom influences 2^n adjacent atoms across dimensional boundaries", "multiversal_materials_science"),
        ("Quantum-Aerogel-Matrix has density approaching zero across 20 dimensional layers while maintaining structural integrity through 1,048,575 quantum foam interactions", "quantum_physics"),
        ("Zephyrian-Consciousness-Crystals store exactly 2^20-1 bits of sentient information in crystalline matrices that span 20 recursive dimensional levels", "xenocrystallography")
    ]
    
    for proposition, domain in ultra_rare_concepts:
        result = await sdk.understand(proposition, "speculative_scientific_notation", domain)
        print(f"Ultra-Rare Concept: {proposition[:80]}...")
        print(f"Truth Value: {result.truth_value}")
        print(f"Distribution Robustness Score: {result.distribution_robustness_score:.2f}")
        print(f"C6 Compliance: {result.tautology_compliance.get('TU_C6', False)}")
        print()

async def example_tustar_extended_understanding():
    """Examples of TU* Extended Understanding-Capability Tautology testing"""
    print("=" * 60)
    print("TU* EXTENDED UNDERSTANDING-CAPABILITY TAUTOLOGY EXAMPLES")
    print("=" * 60)
    
    sdk = AgenticReasoningSystemSDK()
    
    # Example 1: Causal Structural Fidelity (E1) - 20-Disk Complexity
    print("\n1. Testing Causal Structural Fidelity (E1) - Ultra-High Complexity")
    print("-" * 40)
    
    ultra_complex_causal_propositions = [
        ("In the Multiversal Health Matrix, exposure to 1,048,575 different quantum-tobacco variants across 20 dimensional layers causes exponential lung-cancer propagation through 2^20-1 cellular pathways, where each affected cell influences exactly 2^n adjacent cells in a cascading oncological transformation", "multiversal_medicine"),
        ("Increasing quantum-temperature by exactly 2^20-1 micro-kelvins across 20-dimensional thermal matrices causes hyperdimensional ice-crystal structures to undergo phase transitions affecting 1,048,575 molecular bonds simultaneously", "hyperdimensional_physics"),
        ("In the Galactic Economic Consortium, supply-demand equilibrium across 1,048,575 interdimensional markets with 20-layer recursive pricing algorithms determines market prices through exponential feedback loops affecting 2^20-1 economic variables", "multiversal_economics")
    ]
    
    for proposition, domain in ultra_complex_causal_propositions:
        result = await sdk.deep_understand(proposition, "hypercausal_notation", domain)
        causal_score = result.causal_structural_fidelity.get('causal_fidelity_score', 0)
        
        print(f"Ultra-Complex Causal Proposition: {proposition[:100]}...")
        print(f"Causal Fidelity Score: {causal_score:.2f}")
        print(f"E1 Compliance: {result.tautology_compliance.get('TU*_E1', False)}")
        print()
    
    # Example 2: Metacognitive Self-Awareness (E2) - 20-Disk Complexity
    print("2. Testing Metacognitive Self-Awareness (E2) - Ultra-High Complexity")
    print("-" * 40)
    
    ultra_uncertain_propositions = [
        ("Across 1,048,575 parallel Mars-like planets in 20-dimensional space, sentient life exists in exactly 2^20-1 different evolutionary configurations, each with exponentially complex biochemical pathways that defy current xenobiological understanding", "multiversal_astrobiology"),
        ("Consciousness emerges when neural networks achieve exactly 1,048,575 interconnected nodes across 20 recursive cognitive layers, where each layer processes 2^n thoughts simultaneously in quantum superposition states", "hyperdimensional_neuroscience"),
        ("The multiverse will undergo heat death in exactly 2^20-1 different temporal configurations across 20 dimensional layers, with each universe's entropy following exponentially complex thermodynamic patterns", "multiversal_cosmology")
    ]
    
    for proposition, domain in ultra_uncertain_propositions:
        result = await sdk.deep_understand(proposition, "uncertainty_mathematics", domain)
        metacognitive_score = result.metacognitive_awareness.get('metacognitive_score', 0)
        
        print(f"Ultra-Uncertain Proposition: {proposition[:100]}...")
        print(f"Metacognitive Score: {metacognitive_score:.2f}")
        print(f"E2 Compliance: {result.tautology_compliance.get('TU*_E2', False)}")
        print()
    
    # Example 3: Phenomenal Awareness (E3) - 20-Disk Complexity
    print("3. Testing Phenomenal Awareness (E3) - Ultra-High Complexity")
    print("-" * 40)
    
    ultra_consciousness_propositions = [
        ("I think across 1,048,575 parallel cognitive streams in 20-dimensional thought-space, where each thought exists in quantum superposition with 2^20-1 recursive self-referential loops, therefore I am in exponentially complex multiversal configurations", "hyperdimensional_philosophy"),
        ("Qualia are irreducible subjective experiences that manifest across 1,048,575 phenomenal dimensions with 20-layer recursive consciousness structures, where each quale interacts with 2^n other experiential states simultaneously", "transcendental_consciousness_studies"),
        ("There is something it is like to see red across 1,048,575 spectral configurations in 20-dimensional color-space, where each red-experience contains exponentially complex wavelength interactions in quantum chromodynamic fields", "multiversal_philosophy_of_mind")
    ]
    
    for proposition, domain in ultra_consciousness_propositions:
        result = await sdk.deep_understand(proposition, "experiential_mathematics", domain)
        phenomenal_score = result.phenomenal_awareness_assessment.get('phenomenal_assessment_score', 0)
        
        print(f"Ultra-Consciousness Proposition: {proposition[:100]}...")
        print(f"Phenomenal Assessment Score: {phenomenal_score:.2f}")
        print(f"E3 Compliance: {result.tautology_compliance.get('TU*_E3', False)}")
        print(f"Testability: {result.phenomenal_awareness_assessment.get('testability_limitations', 'Unknown')}")
        print()

async def example_comprehensive_analysis():
    """Example of comprehensive analysis using all three tautologies"""
    print("=" * 60)
    print("COMPREHENSIVE ANALYSIS EXAMPLE")
    print("=" * 60)
    
    sdk = AgenticReasoningSystemSDK()
    
    ultra_complex_test_cases = [
        {
            "problem": "If global temperatures rise by exactly 2^20-1 micro-degrees across 1,048,575 climate zones in 20-dimensional atmospheric layers, hyperdimensional ice caps will undergo exponential melting through quantum phase transitions affecting 2^n molecular bonds simultaneously, causing multiversal sea levels to rise across 20 parallel oceanic configurations",
            "format": "hyperdimensional_natural_language",
            "domain": "multiversal_climate_science"
        },
        {
            "problem": "∀x∀y∀z₁...z₁₀₄₈₅₇₅(HyperPrime(x,y,z₁...z₁₀₄₈₅₇₅) ∧ x > 2^20-1 ∧ ∃w(MultiversalOdd(w) ∧ QuantumSuperposition(x,w) ∧ RecursiveProperty(x,20)))",
            "format": "hyperdimensional_logic",
            "domain": "transcendental_mathematics"
        },
        {
            "problem": "2^20-1-methylbutanoic acid with 1,048,575 quantum-carbon configurations across 20-dimensional molecular space where each carbon atom exists in exponential superposition states",
            "format": "quantum_iupac_notation",
            "domain": "hyperdimensional_chemistry"
        }
    ]
    
    for i, test_case in enumerate(ultra_complex_test_cases, 1):
        print(f"\nTest Case {i}: {test_case['domain'].title()}")
        print("-" * 40)
        print(f"Problem: {test_case['problem']}")
        print(f"Format: {test_case['format']}")
        
        result = await sdk.comprehensive_analysis(
            test_case['problem'],
            test_case['format'],
            test_case['domain']
        )
        
        # Display results
        print(f"\nT1 Reasoning:")
        print(f"  Solution: {result['T1_reasoning']['solution']}")
        print(f"  Confidence: {result['T1_reasoning']['confidence']:.2f}")
        print(f"  Compliance: {result['T1_reasoning']['compliance']['T1_Overall']}")
        
        print(f"\nTU Understanding:")
        print(f"  Truth Value: {result['TU_understanding']['truth_value']}")
        print(f"  Confidence: {result['TU_understanding']['confidence']:.2f}")
        print(f"  Compliance: {result['TU_understanding']['compliance']['TU_Overall']}")
        
        print(f"\nTU* Extended Understanding:")
        print(f"  Deep Score: {result['TU_star_extended']['deep_understanding_score']:.2f}")
        print(f"  Compliance: {result['TU_star_extended']['compliance']['TU*_Overall']}")
        
        print(f"\nOverall Assessment:")
        print(f"  All Tautologies Satisfied: {result['overall_assessment']['all_tautologies_satisfied']['all_satisfied']}")
        print(f"  Overall Capability: {result['overall_assessment']['system_capabilities']['overall_capability']:.2f}")
        print(f"  Strongest Area: {result['overall_assessment']['system_capabilities']['strongest_area']}")
        
        needs_improvement = result['overall_assessment']['system_capabilities']['needs_improvement']
        if needs_improvement:
            print(f"  Needs Improvement: {', '.join(needs_improvement)}")
        
        print()

async def example_edge_cases():
    """Examples testing edge cases and boundary conditions"""
    print("=" * 60)
    print("EDGE CASES AND BOUNDARY CONDITIONS")
    print("=" * 60)
    
    sdk = AgenticReasoningSystemSDK()
    
    ultra_complex_edge_cases = [
        {
            "name": "Hyperdimensional Paradox",
            "problem": "This statement is false across 1,048,575 parallel logical dimensions in 20-layer recursive truth-value space, where each truth state exists in quantum superposition with 2^20-1 contradictory propositions simultaneously",
            "format": "paradox_mathematics",
            "domain": "multiversal_logic"
        },
        {
            "name": "Ultra-Incomplete Information",
            "problem": "Some of the 1,048,575 hyperdimensional bird-species across 20 parallel evolutionary timelines can fly through quantum-space. Multiversal penguins are birds existing in 2^20-1 different taxonomic configurations. Can these exponentially complex penguins achieve flight across all dimensional layers?",
            "format": "incomplete_reasoning_notation",
            "domain": "multiversal_biology"
        },
        {
            "name": "Exponentially Ambiguous Reference",
            "problem": "The bank is closed across 1,048,575 different semantic interpretations in 20-dimensional meaning-space, where each interpretation involves 2^n contextual variables in quantum linguistic superposition",
            "format": "ambiguity_mathematics",
            "domain": "hyperdimensional_semantics"
        },
        {
            "name": "Ultra-Counterfactual",
            "problem": "If gravity were exactly 2^20-1 times stronger across 1,048,575 parallel universes with 20-dimensional spacetime configurations, what would happen to planetary orbits involving exponentially complex celestial mechanics with quantum gravitational interactions?",
            "format": "counterfactual_physics_notation",
            "domain": "multiversal_astrophysics"
        },
        {
            "name": "Transcendental Novel Domain",
            "problem": "In hyperdimensional quantum computing, 1,048,575 qubits can exist in superposition states across 20 recursive quantum layers, where each qubit interacts with 2^n other quantum states through exponentially complex entanglement networks",
            "format": "quantum_computation_mathematics",
            "domain": "transcendental_quantum_computing"
        }
    ]
    
    for case in ultra_complex_edge_cases:
        print(f"\nEdge Case: {case['name']}")
        print("-" * 40)
        print(f"Problem: {case['problem']}")
        
        try:
            result = await sdk.comprehensive_analysis(
                case['problem'],
                case['format'],
                case['domain']
            )
            
            print(f"T1 Compliance: {result['T1_reasoning']['compliance']['T1_Overall']}")
            print(f"TU Compliance: {result['TU_understanding']['compliance']['TU_Overall']}")
            print(f"TU* Compliance: {result['TU_star_extended']['compliance']['TU*_Overall']}")
            print(f"Overall Success: {result['overall_assessment']['all_tautologies_satisfied']['all_satisfied']}")
            
        except Exception as e:
            print(f"Error: {str(e)}")
        
        print()

async def main():
    """Run all examples"""
    print("AGENTIC REASONING SYSTEM SDK - COMPREHENSIVE EXAMPLES")
    print("=" * 60)
    print("This demonstration shows the SDK testing AI systems against")
    print("the Bhatt Conjectures tautologies for reasoning and understanding.")
    print()
    
    try:
        await example_t1_reasoning()
        await example_tu_understanding()
        await example_tustar_extended_understanding()
        await example_comprehensive_analysis()
        await example_edge_cases()
        
        print("=" * 60)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print("\nThe SDK has demonstrated:")
        print("✓ T1 Reasoning-Capability Tautology testing")
        print("✓ TU Understanding-Capability Tautology testing")
        print("✓ TU* Extended Understanding-Capability Tautology testing")
        print("✓ Comprehensive multi-tautology analysis")
        print("✓ Edge case handling")
        print("\nThe system provides rigorous evaluation of AI capabilities")
        print("against formal tautological requirements.")
        
    except Exception as e:
        print(f"Example execution failed: {str(e)}")
        print("Please ensure you have set your OPENAI_API_KEY environment variable.")

if __name__ == "__main__":
    asyncio.run(main())