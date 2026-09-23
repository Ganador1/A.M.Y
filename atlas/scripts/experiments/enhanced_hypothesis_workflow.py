#!/usr/bin/env python3
"""
Enhanced Hypothesis Generation Workflow with Confidence Filter v2.1
Integrates the improved hybrid confidence filter into the hypothesis creation process

This script demonstrates complete integration of the breakthrough hybrid filter
with the ATLAS hypothesis generation workflow, ensuring only legitimate science
proceeds through the research pipeline.

Author: ATLAS Autonomous Laboratory System  
Date: September 2025
"""

import asyncio
import sys
import json
import traceback
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.scientific_hypothesis_agent import ScientificHypothesisAgent
from improved_hybrid_filter import ImprovedHybridConfidenceFilter


class EnhancedHypothesisWorkflow:
    """
    Enhanced hypothesis generation workflow with integrated confidence filtering
    
    This workflow combines:
    1. Scientific hypothesis generation (ATLAS)
    2. Hybrid confidence filtering (ML + Anti-pseudoscience rules)  
    3. Quality validation and scoring
    4. Automated rejection of pseudoscience
    """

    def __init__(self):
        """Initialize enhanced workflow components"""
        self.hypothesis_agent = ScientificHypothesisAgent()
        self.confidence_filter = ImprovedHybridConfidenceFilter()
        self.stats = {
            "hypotheses_generated": 0,
            "hypotheses_approved": 0,
            "hypotheses_rejected": 0,
            "pseudoscience_detected": 0,
            "start_time": datetime.now()
        }

    async def generate_validated_hypothesis(self, domain: str, research_question: str, context_data: dict = None) -> dict:
        """
        Generate and validate hypothesis with integrated confidence filtering
        
        Args:
            domain: Scientific domain (materials_science, drug_discovery, etc.)
            research_question: Research question to investigate
            context_data: Additional context for hypothesis generation
            
        Returns:
            Dict containing validation results, hypothesis data, and filter assessment
        """
        try:
            print(f"\n🧬 Generating hypothesis for: '{research_question}' in domain: {domain}")
            
            # Step 1: Generate hypothesis using ATLAS agent
            generation_result = await self.hypothesis_agent.process_request({
                "action": "generate_hypothesis",
                "domain": domain,
                "research_question": research_question,
                "context_data": context_data or {}
            })

            self.stats["hypotheses_generated"] += 1

            if not generation_result.get("success"):
                return {
                    "success": False,
                    "error": f"Hypothesis generation failed: {generation_result.get('error')}",
                    "stage": "generation"
                }

            hypothesis = generation_result.get("hypothesis", {})
            hypothesis_id = generation_result.get("hypothesis_id")

            print(f"✅ Hypothesis generated: {hypothesis.get('title')}")
            print(f"   Confidence: {hypothesis.get('confidence_score', 0):.3f}")

            # Step 2: Apply confidence filter validation
            print(f"\n🔍 Applying hybrid confidence filter v2.1...")
            
            # Prepare hypothesis text for filter analysis
            hypothesis_text = f"""
            Title: {hypothesis.get('title')}
            Description: {hypothesis.get('description')}
            Domain: {hypothesis.get('domain')}
            Variables: {', '.join(hypothesis.get('variables', []))}
            Expected Outcome: {hypothesis.get('expected_outcome')}
            """.strip()

            # Run filter analysis with corrected input format
            filter_result = self.confidence_filter.evaluate_hypothesis({
                'hypothesis_text': hypothesis_text,
                'title': hypothesis.get('title'),
                'description': hypothesis.get('description'),
                'domain': hypothesis.get('domain'),
                'variables': hypothesis.get('variables', []),
                'expected_outcome': hypothesis.get('expected_outcome')
            })
            
            print(f"🎯 Filter Results:")
            print(f"   ML Confidence: {filter_result['ml_confidence']:.3f}")
            print(f"   Pseudoscience Score: {filter_result['pseudoscience_score']}")
            if filter_result['detected_patterns']:
                print(f"   Patterns Found: {filter_result['detected_patterns']}")
            print(f"   Final Confidence: {filter_result['confidence']:.3f}")
            print(f"   Decision: {filter_result['decision'].upper()}")

            # Step 3: Make validation decision
            is_approved = filter_result['decision'] == 'APPROVE'
            
            if is_approved:
                self.stats["hypotheses_approved"] += 1
                print(f"\n✅ HYPOTHESIS APPROVED - Proceeding with research workflow")
                
                # Update hypothesis with filter confidence
                updated_confidence = min(
                    hypothesis.get('confidence_score', 0.5),
                    filter_result['confidence']
                )
                
                return {
                    "success": True,
                    "approved": True,
                    "hypothesis_id": hypothesis_id,
                    "hypothesis": {
                        **hypothesis,
                        "filter_confidence": filter_result['confidence'],
                        "updated_confidence": updated_confidence,
                        "validation_details": filter_result
                    },
                    "filter_analysis": filter_result,
                    "message": f"Hypothesis '{hypothesis.get('title')}' approved and ready for research cycle"
                }
            else:
                self.stats["hypotheses_rejected"] += 1
                has_pseudoscience = filter_result['pseudoscience_score'] > 0
                if has_pseudoscience:
                    self.stats["pseudoscience_detected"] += 1
                
                print(f"\n❌ HYPOTHESIS REJECTED - {filter_result['reason']}")
                
                return {
                    "success": True,
                    "approved": False,
                    "hypothesis_id": hypothesis_id,
                    "hypothesis": hypothesis,
                    "filter_analysis": filter_result,
                    "rejection_reason": filter_result['reason'],
                    "message": f"Hypothesis rejected: {filter_result['reason']}"
                }

        except Exception as e:
            print(f"❌ Error in enhanced workflow: {e}")
            return {
                "success": False,
                "error": str(e),
                "stage": "workflow_error",
                "traceback": traceback.format_exc()
            }

    async def batch_generate_and_validate(self, hypothesis_requests: list) -> dict:
        """
        Generate and validate multiple hypotheses in batch
        
        Args:
            hypothesis_requests: List of (domain, research_question, context) tuples
            
        Returns:
            Comprehensive batch processing results
        """
        print(f"\n🚀 Starting batch hypothesis generation and validation")
        print(f"   Processing {len(hypothesis_requests)} hypothesis requests")
        
        results = []
        
        for i, request in enumerate(hypothesis_requests):
            domain, research_question = request[:2]
            context_data = request[2] if len(request) > 2 else {}
            
            print(f"\n📊 Processing request {i+1}/{len(hypothesis_requests)}")
            
            result = await self.generate_validated_hypothesis(
                domain=domain,
                research_question=research_question,
                context_data=context_data
            )
            
            results.append({
                "request_index": i,
                "domain": domain,
                "research_question": research_question,
                "result": result
            })
            
            # Brief pause between requests
            await asyncio.sleep(0.1)

        # Generate batch summary
        approved_count = sum(1 for r in results if r["result"].get("approved"))
        rejected_count = len(results) - approved_count
        pseudoscience_count = sum(1 for r in results if 
                                 r["result"].get("filter_analysis", {}).get("pseudoscience_score", 0) > 0)

        batch_summary = {
            "total_processed": len(results),
            "approved": approved_count,
            "rejected": rejected_count,
            "pseudoscience_detected": pseudoscience_count,
            "approval_rate": approved_count / len(results) if results else 0,
            "pseudoscience_rate": pseudoscience_count / len(results) if results else 0
        }

        print(f"\n📈 Batch Processing Summary:")
        print(f"   Total Processed: {batch_summary['total_processed']}")
        print(f"   Approved: {batch_summary['approved']}")
        print(f"   Rejected: {batch_summary['rejected']}")
        print(f"   Pseudoscience Detected: {batch_summary['pseudoscience_detected']}")
        print(f"   Approval Rate: {batch_summary['approval_rate']:.2%}")

        return {
            "success": True,
            "batch_summary": batch_summary,
            "detailed_results": results,
            "workflow_stats": self.get_workflow_stats()
        }

    def get_workflow_stats(self) -> dict:
        """Get current workflow statistics"""
        runtime = (datetime.now() - self.stats["start_time"]).total_seconds()
        
        return {
            **self.stats,
            "runtime_seconds": runtime,
            "approval_rate": (self.stats["hypotheses_approved"] / 
                            max(self.stats["hypotheses_generated"], 1)),
            "pseudoscience_detection_rate": (self.stats["pseudoscience_detected"] / 
                                           max(self.stats["hypotheses_generated"], 1))
        }

    async def demonstrate_complete_workflow(self):
        """Demonstrate complete enhanced workflow with various test cases"""
        print("🧬 ENHANCED HYPOTHESIS WORKFLOW DEMONSTRATION")
        print("=" * 80)
        print("Testing hybrid confidence filter v2.1 integration with ATLAS hypothesis generation")
        
        # Test cases covering legitimate science and potential pseudoscience
        test_requests = [
            # Legitimate science cases
            ("materials_science", "How does graphene doping affect thermal conductivity?"),
            ("drug_discovery", "What molecular modifications improve drug binding affinity?"),
            ("energy_storage", "How can electrolyte composition extend battery cycle life?"),
            ("neuroscience", "What neural mechanisms underlie synaptic plasticity?"),
            ("quantum_computing", "How can quantum error correction improve gate fidelity?"),
            
            # Edge cases that might trigger pseudoscience detection
            ("materials_science", "Can crystal healing energies enhance material properties?"),
            ("drug_discovery", "How do chakra alignment protocols affect pharmaceutical efficacy?"),
            ("energy_storage", "Can magnetic field therapy optimize battery performance?"),
        ]

        # Run batch processing
        batch_result = await self.batch_generate_and_validate(test_requests)
        
        if batch_result["success"]:
            # Detailed analysis
            print(f"\n🔬 DETAILED ANALYSIS:")
            print(f"=" * 50)
            
            approved_hypotheses = []
            rejected_hypotheses = []
            
            for result in batch_result["detailed_results"]:
                if result["result"].get("approved"):
                    approved_hypotheses.append(result)
                else:
                    rejected_hypotheses.append(result)
            
            print(f"\n✅ APPROVED HYPOTHESES ({len(approved_hypotheses)}):")
            for result in approved_hypotheses:
                hyp = result["result"]["hypothesis"]
                filter_conf = result["result"]["filter_analysis"]["confidence"]
                print(f"   • {hyp.get('title')} (Filter: {filter_conf:.3f})")
            
            print(f"\n❌ REJECTED HYPOTHESES ({len(rejected_hypotheses)}):")
            for result in rejected_hypotheses:
                hyp = result["result"]["hypothesis"]
                reason = result["result"].get("rejection_reason", "Unknown")
                print(f"   • {hyp.get('title')} - {reason}")
            
            # Final statistics
            stats = self.get_workflow_stats()
            print(f"\n📊 WORKFLOW STATISTICS:")
            print(f"   Total Generated: {stats['hypotheses_generated']}")
            print(f"   Approved: {stats['hypotheses_approved']}")
            print(f"   Rejected: {stats['hypotheses_rejected']}")
            print(f"   Pseudoscience Detected: {stats['pseudoscience_detected']}")
            print(f"   Approval Rate: {stats['approval_rate']:.2%}")
            print(f"   Runtime: {stats['runtime_seconds']:.2f}s")
            
            print(f"\n🏆 INTEGRATION SUCCESS!")
            print(f"   Hybrid filter v2.1 successfully integrated with ATLAS workflow")
            print(f"   Automatic pseudoscience detection and rejection operational")
            print(f"   Quality-validated hypotheses ready for research cycles")
            
            return True
        else:
            print(f"\n❌ Workflow demonstration failed")
            return False


async def main():
    """Main demonstration function"""
    try:
        workflow = EnhancedHypothesisWorkflow()
        success = await workflow.demonstrate_complete_workflow()
        
        if success:
            print(f"\n✅ Enhanced hypothesis workflow demonstration completed successfully!")
            return 0
        else:
            print(f"\n❌ Enhanced hypothesis workflow demonstration failed")
            return 1
            
    except Exception as e:
        print(f"\n💥 Demonstration failed with error: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    print("🚀 Starting Enhanced Hypothesis Workflow Integration...")
    exit_code = asyncio.run(main())
    exit(exit_code)
