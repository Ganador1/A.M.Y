#!/usr/bin/env python3
import asyncio
import sys
from datetime import datetime

# Setup path
sys.path.insert(0, "/Volumes/Ganador disk/atlas")

async def analyze_scores():
    from app.services.verification.autonomous_peer_review_service import AutonomousPeerReviewService, ScientificDomain
    
    service = AutonomousPeerReviewService()
    
    agent_name = "mathematical_reviewer"
    agent_config = {
        "domain": ScientificDomain.MATHEMATICS,
        "expertise": ["proofs", "number theory"],
        "validation_focus": ["logical consistency", "mathematical rigor"]
    }
    
    hypothesis = "The gap between consecutive primes p_n and p_{n+1} is always less than log(p_n)^2 (extended Cramer's conjecture)."
    methodology = "Computational verification up to 10^16 using a distributed prime sieve and Gap-Search algorithm. Statistical analysis of gap distribution compared to Poisson process."
    results = {
        "max_gap_found": 1476,
        "p_value": 0.001,
        "statistics": "Normal distribution of gaps observed in log-scale"
    }
    
    print(f"--- Analyzing Peer Review for Hypothesis ---")
    print(f"Hypothesis: {hypothesis[:100]}...")
    
    review = await service._simulate_peer_review(
        agent_name=agent_name,
        agent_config=agent_config,
        experiment_id="test-exp-123",
        hypothesis=hypothesis,
        methodology=methodology,
        results=results
    )
    
    print(f"\n--- SCORES ---")
    print(f"Overall Score:        {review.overall_score} / 10.0")
    print(f"Scientific Validity:  {review.scientific_validity} / 10.0")
    print(f"Methodological Rigor: {review.methodological_rigor} / 10.0")
    print(f"Novelty Contribution: {review.novelty_contribution} / 10.0")
    
    print(f"\n--- STATUS ---")
    print(f"Approved: {'✅ YES' if review.approved else '❌ NO'}")
    
    if review.issues:
        print(f"\n--- ISSUES ({len(review.issues)}) ---")
        for issue in review.issues:
            print(f"- [{issue.severity.value}] {issue.category}: {issue.description}")

if __name__ == "__main__":
    asyncio.run(analyze_scores())
