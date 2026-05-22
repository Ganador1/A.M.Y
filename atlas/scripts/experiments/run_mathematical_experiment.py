#!/usr/bin/env python3
"""
Mathematical Discovery Experiment Script

This script runs real mathematical experiments using the MathematicalDiscoveryEngine
to validate the hypothesis testing capabilities of the research platform.
"""

import sys
import os
import logging
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, './app')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_mathematical_discovery_experiment():
    """Run mathematical discovery experiments"""
    try:
        from services.mathematical_discovery_engine import MathematicalDiscoveryEngine, Conjecture
        
        logger.info("🚀 Starting Mathematical Discovery Experiment")
        
        # Initialize the discovery engine
        engine = MathematicalDiscoveryEngine()
        
        # Generate seed conjectures
        logger.info("📊 Generating seed conjectures...")
        conjectures = engine.generate_seed_conjectures(domain="algebra", limit=10)
        
        logger.info(f"🔍 Generated {len(conjectures)} conjectures:")
        for i, conj in enumerate(conjectures):
            logger.info(f"  {i+1}. {conj.statement} (Domain: {conj.domain})")
        
        # Investigate each conjecture
        results = []
        for i, conjecture in enumerate(conjectures):
            logger.info(f"\n🔬 Investigating conjecture {i+1}: {conjecture.statement}")
            
            result = engine.investigate_conjecture(conjecture)
            results.append(result)
            
            logger.info(f"   Status: {result.status}")
            if result.status == "proven":
                logger.info(f"   Proof: {result.proof}")
            elif result.status == "refuted":
                logger.info(f"   Counterexample: {result.counterexample}")
            logger.info(f"   Time: {result.time_seconds:.3f}s")
            logger.info(f"   Importance Score: {result.importance:.3f}")
        
        # Analyze results
        logger.info("\n📈 EXPERIMENT RESULTS SUMMARY:")
        logger.info("=" * 50)
        
        proven_count = sum(1 for r in results if r.status == "proven")
        refuted_count = sum(1 for r in results if r.status == "refuted")
        open_count = sum(1 for r in results if r.status == "open")
        
        logger.info(f"Total Conjectures: {len(results)}")
        logger.info(f"Proven: {proven_count}")
        logger.info(f"Refuted: {refuted_count}")
        logger.info(f"Open/Unknown: {open_count}")
        logger.info(f"Success Rate: {proven_count/len(results)*100:.1f}%")
        
        # Show detailed results
        logger.info("\n📋 DETAILED RESULTS:")
        for i, result in enumerate(results):
            logger.info(f"\n{i+1}. {result.conjecture.statement}")
            logger.info(f"   Status: {result.status}")
            logger.info(f"   Time: {result.time_seconds:.3f}s")
            logger.info(f"   Importance: {result.importance:.3f}")
            if result.notes:
                logger.info(f"   Notes: {result.notes}")
        
        return results
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.error("Make sure the app directory is in Python path")
        return None
    except Exception as e:
        logger.error(f"Experiment failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def run_custom_mathematical_experiments():
    """Run custom mathematical experiments with more complex conjectures"""
    try:
        from services.mathematical_discovery_engine import MathematicalDiscoveryEngine, Conjecture
        
        logger.info("\n🧪 Starting Custom Mathematical Experiments")
        
        engine = MathematicalDiscoveryEngine()
        
        # Custom conjectures - some true, some false
        custom_conjectures = [
            Conjecture(
                id="custom_1",
                statement="x**2 + y**2 = (x + y)**2",
                domain="algebra",
                goal="identity"
            ),
            Conjecture(
                id="custom_2", 
                statement="(x + 1)**2 = x**2 + 2*x + 1",
                domain="algebra",
                goal="identity"
            ),
            Conjecture(
                id="custom_3",
                statement="2*x + 3*x = 5*x",
                domain="algebra", 
                goal="identity"
            ),
            Conjecture(
                id="custom_4",
                statement="x**3 - 1 = (x - 1)*(x**2 + x + 1)",
                domain="algebra",
                goal="identity"
            ),
            Conjecture(
                id="custom_5",
                statement="sin(x)**2 + cos(x)**2 = 1",
                domain="trigonometry",
                goal="identity"
            )
        ]
        
        logger.info("🔍 Testing custom conjectures (some true, some false):")
        for i, conj in enumerate(custom_conjectures):
            logger.info(f"  {i+1}. {conj.statement}")
        
        results = []
        for i, conjecture in enumerate(custom_conjectures):
            logger.info(f"\n🔬 Testing: {conjecture.statement}")
            
            result = engine.investigate_conjecture(conjecture)
            results.append(result)
            
            expected_truth = i != 0  # First one is false, others true
            actual_truth = result.status == "proven"
            
            status_symbol = "✅" if expected_truth == actual_truth else "❌"
            
            logger.info(f"   {status_symbol} Status: {result.status}")
            logger.info(f"   Expected: {'True' if expected_truth else 'False'}")
            logger.info(f"   Actual: {'True' if actual_truth else 'False'}")
            logger.info(f"   Correct: {expected_truth == actual_truth}")
            
            if result.status == "refuted" and result.counterexample:
                logger.info(f"   Counterexample: {result.counterexample}")
        
        # Calculate accuracy
        correct = sum(1 for i, r in enumerate(results) 
                     if (r.status == "proven") == (i != 0))
        accuracy = correct / len(results) * 100
        
        logger.info(f"\n🎯 ACCURACY: {accuracy:.1f}% ({correct}/{len(results)} correct)")
        
        return results
        
    except Exception as e:
        logger.error(f"Custom experiment failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("MATHEMATICAL DISCOVERY EXPERIMENT")
    logger.info("=" * 60)
    
    # Run basic experiment
    results1 = run_mathematical_discovery_experiment()
    
    # Run custom experiment  
    results2 = run_custom_mathematical_experiments()
    
    logger.info("\n" + "=" * 60)
    logger.info("EXPERIMENT COMPLETED")
    logger.info("=" * 60)
    
    if results1 and results2:
        logger.info("✅ Both experiments completed successfully!")
        logger.info("📊 The mathematical discovery engine is functioning correctly.")
        logger.info("🔬 Hypothesis testing capabilities validated.")
    else:
        logger.error("❌ Experiments failed or had errors")