#!/usr/bin/env python3
"""
Full Autonomous Research Cycle Simulation
-----------------------------------------
This script demonstrates a complete scientific research loop using:
1. Groq-powered AI Agents (ScientificAIService)
2. Real Scientific Tools (SymPy, NumPy, ArXiv)
3. Autonomous Peer Review

Phases:
1. Hypothesis Generation
2. Experimental Validation (using Real Tools)
3. Paper Drafting
4. Peer Review
"""

import asyncio
import sys
import os
import json
from typing import List, Dict, Any
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.getcwd())

# Import services
from app.services.scientific_ai.scientific_ai import ScientificAIService
from app.services.llm_providers.groq_provider import groq_provider

# Import real tools
import sympy
import numpy as np
try:
    import arxiv
    ARXIV_AVAILABLE = True
except ImportError:
    ARXIV_AVAILABLE = False

# Real Tool Implementations
def real_equation_solver(query: str) -> str:
    """Solves mathematical equations using SymPy"""
    print(f"   [Tool] Solving equation: {query}")
    try:
        # Basic parsing and solving
        # Expecting query like "x**2 - 4 = 0"
        if "=" in query:
            lhs, rhs = query.split("=")
            expr = sympy.sympify(lhs) - sympy.sympify(rhs)
        else:
            expr = sympy.sympify(query)
        
        solution = sympy.solve(expr)
        return f"Solution: {solution}"
    except Exception as e:
        return f"Error solving equation: {str(e)}"

def real_data_analyzer(query: str) -> str:
    """Analyzes data using NumPy"""
    print(f"   [Tool] Analyzing data: {query}")
    try:
        # Generate some synthetic data for demonstration if query asks for it
        if "distribution" in query.lower():
            data = np.random.normal(0, 1, 1000)
            mean = np.mean(data)
            std = np.std(data)
            return f"Generated normal distribution (n=1000). Mean: {mean:.4f}, Std: {std:.4f}"
        return "Data analysis capability ready. Please specify analysis type."
    except Exception as e:
        return f"Error analyzing data: {str(e)}"

async def run_research_iteration(iteration: int, previous_feedback: str = None):
    print(f"\n🔄 Starting Research Iteration {iteration}")
    print("=" * 60)
    
    # 2. Hypothesis Generation
    print(f"\n2️⃣ Phase 1: Hypothesis Generation (Iteration {iteration})")
    print("-" * 60)
    
    topic = "mathematical patterns in prime gaps"
    
    if previous_feedback:
        print(f"   ℹ️ Incorporating feedback from previous iteration...")
        prompt = f"""Refine the previous hypothesis about {topic} based on this reviewer feedback:
        
        Feedback:
        {previous_feedback}
        
        Generate a specific, testable mathematical hypothesis.
        Format:
        Hypothesis: [Statement]
        Mathematical Formulation: [Equation/Inequality]
        Validation Method: [Computational approach]
        """
    else:
        prompt = f"""Generate a specific, testable mathematical hypothesis about {topic}.
        Format:
        Hypothesis: [Statement]
        Mathematical Formulation: [Equation/Inequality]
        Validation Method: [Computational approach]
        """
    
    hypothesis_result = await groq_provider.generate_async(
        prompt=prompt,
        model="llama-3.3-70b-versatile"
    )
    
    if not hypothesis_result.get("success"):
        print("❌ Failed to generate hypothesis")
        return None, None
        
    hypothesis_text = hypothesis_result["text"]
    print(f"📝 Generated Hypothesis:\n{hypothesis_text}")

    # 3. Experimental Validation (Simulation with Real Tools)
    print(f"\n3️⃣ Phase 2: Experimental Validation (Iteration {iteration})")
    print("-" * 60)
    
    # Extract equation to solve (simplified for demo)
    extraction_prompt = f"""Extract a mathematical equation or expression from this hypothesis that can be solved or evaluated symbolically.
    Hypothesis: {hypothesis_text}
    
    Return ONLY the equation (e.g., "x**2 - 4 = 0"). If none, return "N/A".
    """
    
    extraction = await groq_provider.generate_async(
        prompt=extraction_prompt,
        model="llama-3.3-70b-versatile"
    )
    
    equation = extraction["text"].strip()
    print(f"   Target Equation/Expression: {equation}")
    
    experiment_results = ""
    if equation != "N/A" and "zeta" not in equation.lower(): # Avoid complex zeta functions for basic sympy
        print("   🧪 Running SymPy Solver...")
        result = real_equation_solver(equation)
        print(f"   ✅ Result: {result}")
        experiment_results += f"Symbolic Solution Attempt: {result}\n"
        
        # Fallback to numerical if symbolic failed
        if "Error" in result:
             print("   ⚠️ Symbolic solution failed. Falling back to Numerical Simulation...")
             data_result = real_data_analyzer(f"statistical validation for {topic}")
             print(f"   ✅ Numerical Result: {data_result}")
             experiment_results += f"Numerical Simulation: {data_result}\n"
    else:
        print("   ⚠️ No simple symbolic equation found or too complex. Running Numerical Simulation...")
        # Run numerical simulation
        data_result = real_data_analyzer("normal distribution analysis for statistical validation")
        print(f"   ✅ Result: {data_result}")
        experiment_results += f"Numerical Simulation: {data_result}\n"

    # 4. Paper Drafting
    print(f"\n4️⃣ Phase 3: Scientific Paper Drafting (Iteration {iteration})")
    print("-" * 60)
    
    paper_prompt = f"""Write a short scientific paper abstract and results section based on:
    
    Hypothesis:
    {hypothesis_text}
    
    Experimental Results:
    {experiment_results}
    
    Structure:
    1. Abstract
    2. Methodology (Computational)
    3. Results
    4. Conclusion
    """
    
    if previous_feedback:
        paper_prompt += f"\n\nIMPORTANT: Address the following reviewer feedback in the paper:\n{previous_feedback}"
    
    paper_result = await groq_provider.generate_async(
        prompt=paper_prompt,
        model="llama-3.3-70b-versatile"
    )
    
    paper_content = paper_result["text"]
    print(f"📄 Draft Paper:\n{paper_content[:500]}...\n[truncated]")

    # 5. Peer Review
    print(f"\n5️⃣ Phase 4: Autonomous Peer Review (Iteration {iteration})")
    print("-" * 60)
    
    review_prompt = f"""You are a critical scientific reviewer. Review the following paper draft.
    
    Paper:
    {paper_content}
    
    Provide:
    1. Decision (Accept/Reject/Revise)
    2. Scientific Validity Score (1-10)
    3. Critical Flaws (if any)
    4. Recommendations
    """
    
    review_result = await groq_provider.generate_async(
        prompt=review_prompt,
        model="llama-3.3-70b-versatile"
    )
    
    review_text = review_result['text']
    print(f"🧐 Peer Review:\n{review_text}")
    
    return review_text, paper_content

async def run_research_cycle():
    print("🚀 Starting Full Autonomous Research Cycle with Feedback Loop")
    print("=" * 60)

    # 1. Setup Service with Real Tools
    print("\n1️⃣ Initializing Scientific AI Service with Real Tools...")
    service = ScientificAIService()
    print("   - LLM Provider: Groq (llama-3.3-70b-versatile)")
    print("   - Tools: SymPy (Math), NumPy (Data)" + (", ArXiv (Literature)" if ARXIV_AVAILABLE else ""))

    # Iteration 1
    review_text, paper_content = await run_research_iteration(1)
    
    if not review_text:
        return

    # Check if revision is needed
    if "Revise" in review_text or "Reject" in review_text:
        print("\n⚠️ Reviewer requested revision. Starting Iteration 2...")
        
        # Extract recommendations for feedback
        feedback_prompt = f"""Extract the key recommendations and critical flaws from this review to guide the next iteration.
        Review:
        {review_text}
        
        Return a concise list of actionable feedback points.
        """
        
        feedback_result = await groq_provider.generate_async(
            prompt=feedback_prompt,
            model="llama-3.3-70b-versatile"
        )
        
        feedback = feedback_result["text"]
        print(f"   📝 Extracted Feedback:\n{feedback}")
        
        # Iteration 2
        review_text_2, paper_content_2 = await run_research_iteration(2, previous_feedback=feedback)
        
        print("\n📊 Comparison of Iterations:")
        print("   Iteration 1 Review Decision:", "Revise" if "Revise" in review_text else "Accept/Other")
        print("   Iteration 2 Review Decision:", "Revise" if "Revise" in review_text_2 else "Accept/Other")
        
    else:
        print("\n✅ Paper Accepted on first try!")
    
    print("\n" + "=" * 60)
    print("✅ Research Cycle Completed")

if __name__ == "__main__":
    asyncio.run(run_research_cycle())
