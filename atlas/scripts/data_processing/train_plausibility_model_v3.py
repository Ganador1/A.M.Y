#!/usr/bin/env python3
"""
Train multiple plausibility models v3 with real external data.

This script implements multi-architecture training with:
- Real external data from OpenAlex/arXiv/PubMed
- Multiple ML algorithms: LogisticRegression, RandomForest, XGBoost, LightGBM, MLP
- Apple Metal (MPS) acceleration for PyTorch models
- Proper train/validation/holdout splits
- Model comparison leaderboard
- Cross-validation evaluation
- Model persistence and metadata tracking

Usage:
    python train_plausibility_model_v3.py
    python train_plausibility_model_v3.py --dataset data/plausibility_training_v3.jsonl --test-size 0.2
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
import warnings
from dataclasses import dataclass
from datetime import datetime
import pickle

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, accuracy_score, f1_score, brier_score_loss

# Optional advanced models (install via pip)
try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False

try:
    import lightgbm as lgb
    HAS_LIGHTGBM = True
except ImportError:
    HAS_LIGHTGBM = False

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    HAS_TORCH = True
    # Check for Metal Performance Shaders (Apple Silicon)
    HAS_MPS = torch.backends.mps.is_available() if hasattr(torch.backends, 'mps') else False
except ImportError:
    HAS_TORCH = False
    HAS_MPS = False
    nn = None
    optim = None
    torch = None

warnings.filterwarnings('ignore', category=UserWarning)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ModelResult:
    """Container for model training results"""
    name: str
    model: Any
    scaler: Optional[StandardScaler]
    train_scores: Dict[str, float]
    val_scores: Dict[str, float]
    cv_scores: Dict[str, float]
    training_time: float
    inference_time: float
    model_size_mb: float
    feature_names: List[str]
    hyperparameters: Dict[str, Any]

class MLPClassifier(nn.Module):
    """PyTorch MLP for binary classification with MPS support"""
    
    def __init__(self, input_dim: int, hidden_dims: List[int] = [64, 32], dropout: float = 0.2):
        super().__init__()
        layers = []
        prev_dim = input_dim
        
        for hidden_dim in hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.ReLU(),
                nn.Dropout(dropout)
            ])
            prev_dim = hidden_dim
        
        layers.append(nn.Linear(prev_dim, 1))
        layers.append(nn.Sigmoid())
        
        self.network = nn.Sequential(*layers)
    
    def forward(self, x):
        return self.network(x).squeeze()

def load_dataset(filepath: str) -> pd.DataFrame:
    """Load JSONL dataset"""
    records = []
    with open(filepath, 'r') as f:
        for line in f:
            records.append(json.loads(line.strip()))
    
    df = pd.DataFrame(records)
    logger.info(f"Loaded dataset: {len(df)} records, {df['label'].value_counts().to_dict()} class distribution")
    return df

def extract_features(df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    """Extract feature vectors from dataset (same heuristics as service)"""
    features = []
    feature_names = []
    
    # Basic length features
    df['title_len'] = df['title'].str.len()
    df['abstract_len'] = df['abstract'].str.len()
    df['total_len'] = df['title_len'] + df['abstract_len']
    
    features.extend(['title_len', 'abstract_len', 'total_len'])
    feature_names.extend(['title_length', 'abstract_length', 'total_length'])
    
    # Word counts
    df['title_words'] = df['title'].str.split().str.len()
    df['abstract_words'] = df['abstract'].str.split().str.len()
    
    features.extend(['title_words', 'abstract_words'])
    feature_names.extend(['title_word_count', 'abstract_word_count'])
    
    # Scientific indicators (simple heuristics)
    df['has_quantitative'] = df['abstract'].str.contains(r'\b(\d+\.?\d*%|\d+\.?\d*\s*(mg|kg|ml|μg|nm|mm|cm))\b', case=False, regex=True).astype(int)
    df['has_methodology'] = df['abstract'].str.contains(r'\b(method|approach|technique|analysis|experiment)\b', case=False).astype(int)
    df['has_results'] = df['abstract'].str.contains(r'\b(result|finding|show|demonstrate|significant)\b', case=False).astype(int)
    df['has_hypothesis'] = df['abstract'].str.contains(r'\b(hypothesis|hypothesize|propose|suggest)\b', case=False).astype(int)
    
    features.extend(['has_quantitative', 'has_methodology', 'has_results', 'has_hypothesis'])
    feature_names.extend(['has_quantitative', 'has_methodology', 'has_results', 'has_hypothesis'])
    
    # Domain one-hot encoding
    domains = df['domain'].unique()
    for domain in sorted(domains):
        col_name = f'domain_{domain}'
        df[col_name] = (df['domain'] == domain).astype(int)
        features.append(col_name)
        feature_names.append(f'domain_{domain}')
    
    X = df[features].values.astype(np.float32)
    y = df['label'].values.astype(np.float32)
    
    logger.info(f"Extracted features: {X.shape[1]} dimensions")
    return X, y, feature_names

def train_sklearn_model(model, X_train, y_train, X_val, y_val, model_name: str) -> ModelResult:
    """Train sklearn-compatible model"""
    import time
    
    # Use scaler for models that benefit from it
    needs_scaling = model_name in ['LogisticRegression', 'SGDClassifier', 'MLP']
    scaler = StandardScaler() if needs_scaling else None
    
    if scaler:
        X_train_scaled = scaler.fit_transform(X_train)
        X_val_scaled = scaler.transform(X_val)
    else:
        X_train_scaled = X_train
        X_val_scaled = X_val
    
    # Training
    start_time = time.time()
    model.fit(X_train_scaled, y_train)
    training_time = time.time() - start_time
    
    # Predictions
    start_time = time.time()
    train_pred = model.predict_proba(X_train_scaled)[:, 1]
    val_pred = model.predict_proba(X_val_scaled)[:, 1]
    inference_time = (time.time() - start_time) / len(X_val_scaled)
    
    # Scores
    train_scores = {
        'auc': roc_auc_score(y_train, train_pred),
        'accuracy': accuracy_score(y_train, train_pred > 0.5),
        'f1': f1_score(y_train, train_pred > 0.5),
        'brier': brier_score_loss(y_train, train_pred)
    }
    
    val_scores = {
        'auc': roc_auc_score(y_val, val_pred),
        'accuracy': accuracy_score(y_val, val_pred > 0.5),
        'f1': f1_score(y_val, val_pred > 0.5),
        'brier': brier_score_loss(y_val, val_pred)
    }
    
    # Cross-validation
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_auc = cross_val_score(model, X_train_scaled, y_train, cv=cv, scoring='roc_auc')
    cv_f1 = cross_val_score(model, X_train_scaled, y_train, cv=cv, scoring='f1')
    
    cv_scores = {
        'auc_mean': cv_auc.mean(),
        'auc_std': cv_auc.std(),
        'f1_mean': cv_f1.mean(),
        'f1_std': cv_f1.std()
    }
    
    # Model size estimation
    model_size_mb = len(pickle.dumps(model)) / (1024 * 1024)
    
    return ModelResult(
        name=model_name,
        model=model,
        scaler=scaler,
        train_scores=train_scores,
        val_scores=val_scores,
        cv_scores=cv_scores,
        training_time=training_time,
        inference_time=inference_time,
        model_size_mb=model_size_mb,
        feature_names=[], # Will be set later
        hyperparameters=model.get_params() if hasattr(model, 'get_params') else {}
    )

def train_pytorch_mlp(X_train, y_train, X_val, y_val, device: str = 'cpu') -> ModelResult:
    """Train PyTorch MLP with MPS support"""
    if not HAS_TORCH:
        raise RuntimeError("PyTorch not available")
        
    import time
    
    # Scaling
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    
    # Convert to tensors
    X_train_tensor = torch.FloatTensor(X_train_scaled).to(device)
    y_train_tensor = torch.FloatTensor(y_train).to(device)
    X_val_tensor = torch.FloatTensor(X_val_scaled).to(device)
    
    # Model
    model = MLPClassifier(input_dim=X_train.shape[1]).to(device)
    optimizer = optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-4)
    criterion = nn.BCELoss()
    
    # Training
    start_time = time.time()
    model.train()
    
    for epoch in range(100):  # Simple training loop
        optimizer.zero_grad()
        outputs = model(X_train_tensor)
        loss = criterion(outputs, y_train_tensor)
        loss.backward()
        optimizer.step()
    
    training_time = time.time() - start_time
    
    # Evaluation
    model.eval()
    start_time = time.time()
    
    with torch.no_grad():
        train_pred = model(X_train_tensor).cpu().numpy()
        val_pred = model(X_val_tensor).cpu().numpy()
    
    inference_time = (time.time() - start_time) / len(X_val_scaled)
    
    # Scores
    train_scores = {
        'auc': roc_auc_score(y_train, train_pred),
        'accuracy': accuracy_score(y_train, train_pred > 0.5),
        'f1': f1_score(y_train, train_pred > 0.5),
        'brier': brier_score_loss(y_train, train_pred)
    }
    
    val_scores = {
        'auc': roc_auc_score(y_val, val_pred),
        'accuracy': accuracy_score(y_val, val_pred > 0.5),
        'f1': f1_score(y_val, val_pred > 0.5),
        'brier': brier_score_loss(y_val, val_pred)
    }
    
    # Model size
    model_size_mb = sum(p.numel() * 4 for p in model.parameters()) / (1024 * 1024)  # 4 bytes per float32
    
    return ModelResult(
        name='MLP_PyTorch',
        model=(model, scaler),
        scaler=scaler,
        train_scores=train_scores,
        val_scores=val_scores,
        cv_scores={},  # Skip CV for PyTorch models
        training_time=training_time,
        inference_time=inference_time,
        model_size_mb=model_size_mb,
        feature_names=[],
        hyperparameters={'hidden_dims': [64, 32], 'dropout': 0.2, 'lr': 0.001}
    )

def create_models() -> List[Tuple[str, Any]]:
    """Create model instances"""
    models = [
        ('LogisticRegression', LogisticRegression(random_state=42, max_iter=1000, class_weight='balanced')),
        ('RandomForest', RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')),
        ('SGDClassifier', SGDClassifier(random_state=42, class_weight='balanced', loss='log_loss'))
    ]
    
    if HAS_XGBOOST:
        models.append(('XGBoost', xgb.XGBClassifier(random_state=42, eval_metric='logloss')))
    
    if HAS_LIGHTGBM:
        models.append(('LightGBM', lgb.LGBMClassifier(random_state=42, verbose=-1)))
    
    return models

def print_leaderboard(results: List[ModelResult]):
    """Print model comparison leaderboard"""
    print("\n" + "="*80)
    print("🏆 PLAUSIBILITY MODEL v3 LEADERBOARD")
    print("="*80)
    
    # Sort by validation AUC
    results_sorted = sorted(results, key=lambda x: x.val_scores['auc'], reverse=True)
    
    header = f"{'Model':<18} {'Val AUC':<8} {'Val F1':<8} {'Train Time':<10} {'Inf Time':<10} {'Size MB':<8} {'CV AUC':<12}"
    print(header)
    print("-" * len(header))
    
    for i, result in enumerate(results_sorted):
        cv_auc_str = f"{result.cv_scores.get('auc_mean', 0):.3f}±{result.cv_scores.get('auc_std', 0):.3f}" if result.cv_scores else "N/A"
        
        print(f"{result.name:<18} {result.val_scores['auc']:<8.3f} {result.val_scores['f1']:<8.3f} "
              f"{result.training_time:<10.2f} {result.inference_time*1000:<10.2f} {result.model_size_mb:<8.2f} {cv_auc_str:<12}")
    
    print("\n📊 Top Model Details:")
    best = results_sorted[0]
    print(f"🥇 Best Model: {best.name}")
    print(f"   Validation AUC: {best.val_scores['auc']:.4f}")
    print(f"   Validation F1:  {best.val_scores['f1']:.4f}")
    print(f"   Validation Acc: {best.val_scores['accuracy']:.4f}")
    print(f"   Brier Score:    {best.val_scores['brier']:.4f}")
    print(f"   Training Time:  {best.training_time:.2f}s")
    print(f"   Inference Time: {best.inference_time*1000:.2f}ms per sample")

def save_results(results: List[ModelResult], dataset_path: str, output_dir: str = "models"):
    """Save training results and best model"""
    Path(output_dir).mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save leaderboard
    leaderboard = []
    for result in results:
        leaderboard.append({
            'model_name': result.name,
            'val_auc': result.val_scores['auc'],
            'val_f1': result.val_scores['f1'],
            'val_accuracy': result.val_scores['accuracy'],
            'val_brier': result.val_scores['brier'],
            'train_auc': result.train_scores['auc'],
            'cv_auc_mean': result.cv_scores.get('auc_mean', None),
            'cv_auc_std': result.cv_scores.get('auc_std', None),
            'training_time': result.training_time,
            'inference_time': result.inference_time,
            'model_size_mb': result.model_size_mb,
            'hyperparameters': result.hyperparameters
        })
    
    leaderboard_path = Path(output_dir) / f"plausibility_v3_leaderboard_{timestamp}.json"
    with open(leaderboard_path, 'w') as f:
        json.dump({
            'dataset_path': dataset_path,
            'timestamp': timestamp,
            'results': leaderboard
        }, f, indent=2)
    
    # Save best model
    best_result = max(results, key=lambda x: x.val_scores['auc'])
    best_model_path = Path(output_dir) / f"plausibility_v3_best_{timestamp}.pkl"
    
    with open(best_model_path, 'wb') as f:
        pickle.dump({
            'model': best_result.model,
            'scaler': best_result.scaler,
            'feature_names': best_result.feature_names,
            'metadata': {
                'model_name': best_result.name,
                'timestamp': timestamp,
                'dataset_path': dataset_path,
                'validation_scores': best_result.val_scores,
                'hyperparameters': best_result.hyperparameters
            }
        }, f)
    
    logger.info(f"Results saved: {leaderboard_path}")
    logger.info(f"Best model saved: {best_model_path}")

def main():
    parser = argparse.ArgumentParser(description="Train plausibility models v3")
    parser.add_argument("--dataset", default="data/plausibility_training_v3.jsonl")
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--val-size", type=float, default=0.2)
    parser.add_argument("--random-seed", type=int, default=42)
    args = parser.parse_args()
    
    logger.info("🚀 Starting Plausibility Model v3 Training")
    logger.info(f"Dataset: {args.dataset}")
    logger.info(f"PyTorch available: {HAS_TORCH}")
    logger.info(f"MPS available: {HAS_MPS}")
    logger.info(f"XGBoost available: {HAS_XGBOOST}")
    logger.info(f"LightGBM available: {HAS_LIGHTGBM}")
    
    # Load data
    df = load_dataset(args.dataset)
    X, y, feature_names = extract_features(df)
    
    # Train/test split
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=args.random_seed, stratify=y
    )
    
    # Train/val split
    val_size_adjusted = args.val_size / (1 - args.test_size)
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=val_size_adjusted, random_state=args.random_seed, stratify=y_temp
    )
    
    logger.info(f"Splits: Train={len(X_train)}, Val={len(X_val)}, Test={len(X_test)}")
    
    # Train models
    results = []
    models = create_models()
    
    for model_name, model in models:
        logger.info(f"Training {model_name}...")
        try:
            result = train_sklearn_model(model, X_train, y_train, X_val, y_val, model_name)
            result.feature_names = feature_names
            results.append(result)
            logger.info(f"{model_name}: Val AUC={result.val_scores['auc']:.3f}")
        except Exception as e:
            logger.error(f"Failed to train {model_name}: {e}")
    
    # Train PyTorch MLP if available
    if HAS_TORCH:
        device = 'mps' if HAS_MPS else 'cpu'
        logger.info(f"Training MLP on {device}...")
        try:
            mlp_result = train_pytorch_mlp(X_train, y_train, X_val, y_val, device)
            mlp_result.feature_names = feature_names
            results.append(mlp_result)
            logger.info(f"MLP: Val AUC={mlp_result.val_scores['auc']:.3f}")
        except Exception as e:
            logger.error(f"Failed to train MLP: {e}")
    
    # Results
    if results:
        print_leaderboard(results)
        save_results(results, args.dataset)
        logger.info("✅ Training completed successfully")
    else:
        logger.error("❌ No models were trained successfully")

if __name__ == "__main__":
    main()
