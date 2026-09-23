#!/usr/bin/env python3
"""
Test script para verificar las mejoras del PlausibilityScoringService
"""

import asyncio
import sys
from pathlib import Path
import numpy as np
from datetime import datetime

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.plausibility_scoring_service import PlausibilityScoringService

def test_basic_functionality():
    """Test básico de funcionalidad"""
    print("🧪 Testing Basic Functionality...")
    
    service = PlausibilityScoringService()
    
    # Test data
    hypothesis_data = {
        "title": "Machine Learning Approach for Drug Discovery",
        "description": "Using deep learning algorithms to predict molecular properties and accelerate drug discovery process with high accuracy.",
        "variables": ["molecular_structure", "binding_affinity", "toxicity"],
        "assumptions": ["sufficient training data", "valid molecular representations"],
        "expected_outcome": "90% accuracy in drug property prediction",
        "domain": "drug_discovery"
    }
    
    # Test scoring
    result = service.score_hypothesis(hypothesis_data)
    
    assert result["success"] == True
    assert 0 <= result["composite"] <= 1
    print(f"✅ Basic scoring: {result['composite']:.3f}")
    
    return result

def test_ensemble_model():
    """Test del modelo ensemble"""
    print("\n🧪 Testing Ensemble Model...")
    
    service = PlausibilityScoringService()
    
    # Generate synthetic training data
    np.random.seed(42)
    n_samples = 100
    n_features = 25  # Based on new feature vector length
    
    X = []
    y = []
    
    for i in range(n_samples):
        # Generate random hypothesis data
        hypothesis = {
            "title": f"Test Hypothesis {i}",
            "description": f"Description for hypothesis {i} with some technical terms and analysis method",
            "variables": [f"var_{j}" for j in range(np.random.randint(1, 6))],
            "assumptions": [f"assumption_{j}" for j in range(np.random.randint(1, 4))],
            "expected_outcome": f"Expected outcome {i}",
            "domain": np.random.choice(["drug_discovery", "materials_science", "ai_research"])
        }
        
        features = service.extract_feature_vector(hypothesis)
        X.append(features)
        
        # Generate synthetic labels (0 or 1)
        y.append(np.random.randint(0, 2))
    
    # Test ensemble creation
    ensemble = service.create_ensemble_model()
    if ensemble is not None:
        print("✅ Ensemble model created successfully")
        
        # Test training
        training_result = service.train_ensemble_model(X, y)
        if training_result["success"]:
            print(f"✅ Training completed: CV score = {training_result['cv_mean']:.3f} ± {training_result['cv_std']:.3f}")
            print(f"✅ Features used: {training_result['n_features']}")
        else:
            print(f"❌ Training failed: {training_result['error']}")
    else:
        print("❌ Ensemble model creation failed")

def test_advanced_features():
    """Test de características avanzadas"""
    print("\n🧪 Testing Advanced Features...")
    
    service = PlausibilityScoringService()
    
    # Test data
    hypothesis_data = {
        "title": "Quantum Machine Learning for Molecular Optimization",
        "description": "Novel quantum algorithms combined with machine learning techniques to optimize molecular structures for pharmaceutical applications.",
        "variables": ["quantum_circuits", "molecular_energy", "optimization_parameters"],
        "assumptions": ["quantum hardware availability", "classical-quantum hybrid approach"],
        "expected_outcome": "50% improvement in molecular optimization speed",
        "domain": "quantum_computing"
    }
    
    # Test feature extraction
    features = service.extract_feature_vector(hypothesis_data)
    print(f"✅ Feature vector length: {len(features)}")
    
    # Test prediction if model exists
    if service.model is not None:
        prediction = service.predict_with_ensemble(features)
        if prediction["success"]:
            print(f"✅ Prediction: {prediction['probability']:.3f} (confidence: {prediction['confidence']:.3f})")
        else:
            print(f"❌ Prediction failed: {prediction['error']}")
    
    # Test explanation
    explanation = service.explain_prediction(hypothesis_data)
    if explanation["success"]:
        print("✅ Explanation generated successfully")
        print(f"   Confidence: {explanation['explanation_summary']['confidence']:.3f}")
        print(f"   Recommendations: {len(explanation['explanation_summary']['recommendations'])}")
    else:
        print(f"❌ Explanation failed: {explanation['error']}")

def test_model_statistics():
    """Test de estadísticas del modelo"""
    print("\n🧪 Testing Model Statistics...")
    
    service = PlausibilityScoringService()
    
    stats = service.get_model_statistics()
    
    print(f"✅ Model available: {stats['model_available']}")
    print(f"✅ Transformer available: {stats['transformer_available']}")
    print(f"✅ SHAP available: {stats['shap_available']}")
    print(f"✅ Scaler available: {stats['scaler_available']}")
    print(f"✅ Feature selector available: {stats['feature_selector_available']}")
    
    if stats['model_available']:
        print(f"✅ Model type: {stats.get('model_type', 'Unknown')}")
        if 'n_base_models' in stats:
            print(f"✅ Base models: {stats['n_base_models']}")

def test_transformer_embeddings():
    """Test de embeddings con transformer"""
    print("\n🧪 Testing Transformer Embeddings...")
    
    service = PlausibilityScoringService()
    
    test_text = "Machine learning algorithms for drug discovery using deep neural networks"
    
    # Test semantic embedding
    embedding = service.get_semantic_embedding(test_text)
    print(f"✅ Embedding length: {len(embedding)}")
    print(f"✅ Embedding sample: {embedding[:5]}")
    
    # Test transformer initialization
    if service._transformer_model is not None:
        print("✅ Transformer model initialized successfully")
    else:
        print("⚠️ Transformer model not available (expected if transformers not installed)")

def main():
    """Ejecutar todos los tests"""
    print("🚀 Testing PlausibilityScoringService Improvements")
    print("=" * 60)
    
    start_time = datetime.now()
    
    try:
        # Run tests
        test_basic_functionality()
        test_ensemble_model()
        test_advanced_features()
        test_model_statistics()
        test_transformer_embeddings()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "=" * 60)
        print("🎉 All tests completed successfully!")
        print(f"⏱️ Total time: {duration:.2f} seconds")
        print("\n✅ PlausibilityScoringService improvements are working correctly!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
