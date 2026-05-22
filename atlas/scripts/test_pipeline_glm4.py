
import asyncio
import os
import sys
import logging

# Ensure project root is in path
sys.path.insert(0, os.getcwd())

from app.run_agent_with_tools_legacy import autonomous_research_agent
from app.services.verification.autonomous_peer_review_service import AutonomousPeerReviewService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_pipeline")

async def run_real_test():
    print("=" * 80)
    print("🚀 STARTING REAL PIPELINE TEST WITH GLM-4 PEER REVIEW")
    print("=" * 80)
    
    # 1. Configuration
    domain = "mathematics"
    topic = "topological data analysis for time series classification"
    model_agent = "minimax-m2.1:cloud"  # Best for generation
    model_reviewer = "glm-4"            # User requested GLM-4.7 (mapping to glm-4)
    
    print(f"📌 Domain: {domain}")
    print(f"📌 Topic: {topic}")
    print(f"📌 Agent Model: {model_agent}")
    print(f"📌 Reviewer Model: {model_reviewer}")
    
    # 2. Patch Peer Review Service to use specific model
    original_review_method = AutonomousPeerReviewService._intelligent_llm_review
    
    async def patched_review(self, hypothesis, paper_content, domain, model_name=None):
        # Force the requested reviewer model
        print(f"   🧠 Invoking Intelligent Peer Review using {model_reviewer}...")
        return await original_review_method(self, hypothesis, paper_content, domain, model_name=model_reviewer)
    
    AutonomousPeerReviewService._intelligent_llm_review = patched_review
    
    # 3. Run Agent
    print("\nStarting Autonomous Agent...")
    result = await autonomous_research_agent(
        domain=domain,
        topic=topic,
        max_iterations=3,
        target_score=7.5,
        model_name=model_agent
    )
    
    # 4. Analyze Results
    print("\n" + "=" * 80)
    print("📊 TEST RESULTS")
    print("=" * 80)
    
    print(f"Status: {result.get('status')}")
    print(f"Final Score: {result.get('final_score')}")
    print(f"Iterations: {result.get('iterations_used')}")
    
    if result.get('status') == 'accepted':
        print("\n✅ Paper Accepted!")
        
        # Check artifacts
        import glob
        files = glob.glob("artifacts/research_papers/*topological*")
        print("\n📁 Generated Artifacts:")
        for f in files:
            print(f"   - {f}")
            
        # Check ReasoningBank
        from app.memory.reasoning_bank import get_reasoning_bank
        rb = get_reasoning_bank()
        similar = rb.retrieve_similar(topic, domain=domain, k=1)
        if similar:
            print(f"\n🧠 ReasoningBank Verification:")
            print(f"   - Found experience: {similar[0].experience_id}")
            print(f"   - Score stored: {similar[0].score}")
        else:
            print("\n⚠️ Warning: No experience found in ReasoningBank for this topic.")
            
    else:
        print("\n❌ Paper Rejected or Failed")
        print(f"Feedback: {result.get('review')[:500]}...")

if __name__ == "__main__":
    asyncio.run(run_real_test())
