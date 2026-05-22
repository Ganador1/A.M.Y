"""
Scientific AutoML Service

This service provides automated machine learning capabilities specifically designed
for scientific domains including physics, chemistry, biology, and materials science.
It integrates multiple AutoML frameworks and provides domain-specific optimizations.
"""

import logging
import asyncio
import time
from typing import Dict, Any, List, Optional, Union, Tuple
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
import os
from pathlib import Path

from app.services.base_service import BaseService
from app.exceptions.domain.biology import BiologyError
from app.types.scientific_automl_service_types import (
    GetServiceInfoResult,
    ProcessRequestResult,
)

# Framework availability checks
try:
    import autosklearn.classification
    import autosklearn.regression
    AUTOSKLEARN_AVAILABLE = True
except ImportError:
    AUTOSKLEARN_AVAILABLE = False

try:
    from flaml import AutoML as FLAML
    FLAML_AVAILABLE = True
except ImportError:
    FLAML_AVAILABLE = False

try:
    import optuna
    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False

# MLflow for experiment tracking
try:
    import mlflow
    import mlflow.sklearn
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False

# Core ML libraries
try:
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.metrics import accuracy_score, r2_score, mean_squared_error, roc_auc_score
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

logger = logging.getLogger(__name__)


class ScientificAutoMLService(BaseService):
    """
    Advanced AutoML service for scientific domains
    """
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.frameworks = {
            'autosklearn': AUTOSKLEARN_AVAILABLE,
            'flaml': FLAML_AVAILABLE,
            'optuna': OPTUNA_AVAILABLE,
            'mlflow': MLFLOW_AVAILABLE,
            'sklearn': SKLEARN_AVAILABLE
        }
        
        self.model_registry = {}
        self.experiment_cache = {}
        
        # Domain-specific configurations
        self.domain_configs = {
            'physics': {
                'metric': 'r2',
                'time_budget': 600,
                'scale_features': True,
                'preferred_models': ['random_forest', 'gradient_boosting', 'neural_network']
            },
            'chemistry': {
                'metric': 'r2',
                'time_budget': 900,
                'scale_features': True,
                'preferred_models': ['random_forest', 'svm', 'neural_network']
            },
            'biology': {
                'metric': 'accuracy',
                'time_budget': 300,
                'scale_features': False,
                'preferred_models': ['random_forest', 'logistic_regression']
            },
            'materials': {
                'metric': 'r2',
                'time_budget': 1200,
                'scale_features': True,
                'preferred_models': ['gradient_boosting', 'neural_network']
            },
            'general': {
                'metric': 'auto',
                'time_budget': 300,
                'scale_features': True,
                'preferred_models': ['random_forest']
            }
        }

    def get_service_info(self) -> GetServiceInfoResult:
        """Get service information and capabilities"""
        return {
            'name': 'ScientificAutoMLService',
            'version': '2.0.0',
            'description': 'Automated ML for scientific domains',
            'capabilities': [
                'multi_framework_automl',
                'domain_optimization',
                'experiment_tracking',
                'model_registry',
                'ensemble_methods',
                'feature_engineering',
                'transfer_learning'
            ],
            'available_frameworks': {k: v for k, v in self.frameworks.items() if v},
            'supported_domains': list(self.domain_configs.keys())
        }

    async def auto_discover_model(self,
                                  X: pd.DataFrame,
                                  y: pd.Series,
                                  domain: str = 'general',
                                  task_type: str = 'auto',
                                  time_limit: int = 300,
                                  frameworks: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Automatically discover the best model for given data
        """
        start_time = time.time()
        
        try:
            # Auto-detect task type if needed
            if task_type == 'auto':
                task_type = self._detect_task_type(y)
            
            # Get domain configuration
            domain_config = self.domain_configs.get(domain, self.domain_configs['general'])
            
            # Preprocess data
            X_processed, y_processed = self._preprocess_data(X, y, domain_config)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X_processed, y_processed, test_size=0.2, random_state=42
            )
            
            # Determine frameworks to use
            if frameworks is None:
                frameworks = [f for f, available in self.frameworks.items() if available and f != 'mlflow']
            else:
                frameworks = [f for f in frameworks if self.frameworks.get(f, False)]
            
            # Run experiments with different frameworks
            results = {}
            best_score = float('-inf')
            best_model = None
            best_framework = None
            
            time_per_framework = time_limit // len(frameworks) if frameworks else time_limit
            
            for framework in frameworks:
                try:
                    result = await self._run_framework(
                        framework, X_train, X_test, y_train, y_test,
                        task_type, domain_config, time_per_framework
                    )
                    results[framework] = result
                    
                    if result.get('score') and self._is_better_score(result['score'], best_score, task_type):
                        best_score = result['score']
                        best_model = result
                        best_framework = framework
                        
                except BiologyError as e:
                    logger.error(f"Framework {framework} failed: {str(e)}")
                    results[framework] = {'error': str(e), 'score': None}
            
            # Calculate feature importance if possible
            feature_importance = {}
            if best_model and best_model.get('model'):
                feature_importance = self._calculate_feature_importance(
                    best_model['model'], X.columns.tolist()
                )
            
            execution_time = time.time() - start_time
            
            final_result = {
                'domain': domain,
                'task_type': task_type,
                'best_framework': best_framework,
                'best_score': best_score,
                'best_model': best_model,
                'all_results': results,
                'feature_importance': feature_importance,
                'execution_time': execution_time,
                'models_evaluated': len([r for r in results.values() if r.get('score') is not None]),
                'data_shape': X.shape,
                'timestamp': datetime.now().isoformat()
            }
            
            # Log to MLflow if available
            if MLFLOW_AVAILABLE:
                await self._log_to_mlflow(final_result, X, y)
            
            # Store in registry
            if best_model and best_model.get('model'):
                model_id = f"{domain}_{task_type}_{int(time.time())}"
                self.model_registry[model_id] = {
                    'model': best_model['model'],
                    'domain': domain,
                    'task_type': task_type,
                    'score': best_score,
                    'framework': best_framework,
                    'timestamp': datetime.now().isoformat()
                }
                final_result['model_id'] = model_id
            
            return final_result
            
        except BiologyError as e:
            logger.error(f"AutoML discovery failed: {str(e)}")
            return {
                'error': str(e),
                'execution_time': time.time() - start_time,
                'timestamp': datetime.now().isoformat()
            }

    async def _run_framework(self, framework: str, X_train, X_test, y_train, y_test,
                           task_type: str, domain_config: Dict, time_budget: int) -> Dict[str, Any]:
        """Run a specific AutoML framework"""
        
        if framework == 'flaml':
            return await self._run_flaml(X_train, X_test, y_train, y_test, task_type, domain_config, time_budget)
        elif framework == 'autosklearn':
            return await self._run_autosklearn(X_train, X_test, y_train, y_test, task_type, domain_config, time_budget)
        elif framework == 'optuna':
            return await self._run_optuna(X_train, X_test, y_train, y_test, task_type, domain_config, time_budget)
        elif framework == 'sklearn':
            return await self._run_sklearn_baseline(X_train, X_test, y_train, y_test, task_type, domain_config)
        else:
            raise ValueError(f"Unknown framework: {framework}")

    async def _run_flaml(self, X_train, X_test, y_train, y_test, task_type: str, 
                        domain_config: Dict, time_budget: int) -> Dict[str, Any]:
        """Run FLAML AutoML"""
        try:
            automl = FLAML()
            automl.fit(X_train, y_train, task=task_type, time_budget=time_budget)
            
            y_pred = automl.predict(X_test)
            metric = domain_config.get('metric', 'accuracy' if task_type == 'classification' else 'r2')
            score = self._calculate_score(y_test, y_pred, task_type, metric)
            
            return {
                'framework': 'flaml',
                'score': score,
                'model': automl,
                'best_config': automl.best_config,
                'best_estimator': str(automl.best_estimator)
            }
        except BiologyError as e:
            logger.error(f"FLAML failed: {str(e)}")
            return {'error': str(e), 'score': None}

    async def _run_sklearn_baseline(self, X_train, X_test, y_train, y_test, 
                                   task_type: str, domain_config: Dict) -> Dict[str, Any]:
        """Run sklearn baseline model"""
        try:
            if task_type == 'classification':
                model = RandomForestClassifier(n_estimators=100, random_state=42)
            else:
                model = RandomForestRegressor(n_estimators=100, random_state=42)
            
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            
            metric = domain_config.get('metric', 'accuracy' if task_type == 'classification' else 'r2')
            score = self._calculate_score(y_test, y_pred, task_type, metric)
            
            return {
                'framework': 'sklearn',
                'score': score,
                'model': model,
                'model_type': 'RandomForest'
            }
        except BiologyError as e:
            logger.error(f"Sklearn baseline failed: {str(e)}")
            return {'error': str(e), 'score': None}

    async def _run_autosklearn(self, X_train, X_test, y_train, y_test,
                              task_type: str, domain_config: Dict, time_budget: int) -> Dict[str, Any]:
        """Run Auto-sklearn"""
        try:
            if task_type == 'classification':
                automl = autosklearn.classification.AutoSklearnClassifier(
                    time_left_for_this_task=time_budget,
                    per_run_time_limit=time_budget // 10,
                    memory_limit=3072
                )
            else:
                automl = autosklearn.regression.AutoSklearnRegressor(
                    time_left_for_this_task=time_budget,
                    per_run_time_limit=time_budget // 10,
                    memory_limit=3072
                )
            
            automl.fit(X_train, y_train)
            y_pred = automl.predict(X_test)
            
            metric = domain_config.get('metric', 'accuracy' if task_type == 'classification' else 'r2')
            score = self._calculate_score(y_test, y_pred, task_type, metric)
            
            return {
                'framework': 'autosklearn',
                'score': score,
                'model': automl,
                'leaderboard': str(automl.leaderboard()),
                'statistics': str(automl.sprint_statistics())
            }
        except BiologyError as e:
            logger.error(f"Auto-sklearn failed: {str(e)}")
            return {'error': str(e), 'score': None}

    async def _run_optuna(self, X_train, X_test, y_train, y_test,
                         task_type: str, domain_config: Dict, time_budget: int) -> Dict[str, Any]:
        """Run Optuna hyperparameter optimization"""
        try:
            def objective(trial):
                if task_type == 'classification':
                    n_estimators = trial.suggest_int('n_estimators', 10, 200)
                    max_depth = trial.suggest_int('max_depth', 3, 20)
                    model = RandomForestClassifier(
                        n_estimators=n_estimators,
                        max_depth=max_depth,
                        random_state=42
                    )
                else:
                    n_estimators = trial.suggest_int('n_estimators', 10, 200)
                    max_depth = trial.suggest_int('max_depth', 3, 20)
                    model = RandomForestRegressor(
                        n_estimators=n_estimators,
                        max_depth=max_depth,
                        random_state=42
                    )
                
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                
                metric = domain_config.get('metric', 'accuracy' if task_type == 'classification' else 'r2')
                return self._calculate_score(y_test, y_pred, task_type, metric)
            
            study = optuna.create_study(direction='maximize')
            study.optimize(objective, timeout=time_budget)
            
            # Train best model
            best_params = study.best_params
            if task_type == 'classification':
                best_model = RandomForestClassifier(**best_params, random_state=42)
            else:
                best_model = RandomForestRegressor(**best_params, random_state=42)
            
            best_model.fit(X_train, y_train)
            y_pred = best_model.predict(X_test)
            
            metric = domain_config.get('metric', 'accuracy' if task_type == 'classification' else 'r2')
            score = self._calculate_score(y_test, y_pred, task_type, metric)
            
            return {
                'framework': 'optuna',
                'score': score,
                'model': best_model,
                'best_params': best_params,
                'n_trials': len(study.trials),
                'best_value': study.best_value
            }
        except BiologyError as e:
            logger.error(f"Optuna failed: {str(e)}")
            return {'error': str(e), 'score': None}

    def _detect_task_type(self, y: pd.Series) -> str:
        """Auto-detect if task is classification or regression"""
        if y.dtype == 'object' or len(y.unique()) < 20:
            return 'classification'
        else:
            return 'regression'

    def _preprocess_data(self, X: pd.DataFrame, y: pd.Series, domain_config: Dict) -> Tuple[pd.DataFrame, pd.Series]:
        """Preprocess data based on domain configuration"""
        X_processed = X.copy()
        y_processed = y.copy()
        
        # Handle missing values
        X_processed = X_processed.fillna(X_processed.mean(numeric_only=True))
        
        # Encode categorical variables
        for col in X_processed.select_dtypes(include=['object']).columns:
            le = LabelEncoder()
            X_processed[col] = le.fit_transform(X_processed[col].astype(str))
        
        # Scale features for certain domains
        if domain_config.get('scale_features', True):
            scaler = StandardScaler()
            X_processed = pd.DataFrame(
                scaler.fit_transform(X_processed),
                columns=X_processed.columns,
                index=X_processed.index
            )
        
        return X_processed, y_processed

    def _calculate_score(self, y_true, y_pred, task_type: str, metric: str) -> float:
        """Calculate score based on task type and metric"""
        if task_type == 'classification':
            if metric == 'accuracy':
                return accuracy_score(y_true, y_pred)
            elif metric == 'roc_auc':
                return roc_auc_score(y_true, y_pred) if len(np.unique(y_true)) == 2 else accuracy_score(y_true, y_pred)
            else:
                return accuracy_score(y_true, y_pred)
        else:  # regression
            if metric == 'r2':
                return r2_score(y_true, y_pred)
            elif metric == 'mse':
                return -mean_squared_error(y_true, y_pred)  # Negative for maximization
            elif metric == 'mae':
                return -np.mean(np.abs(y_true - y_pred))  # Negative for maximization
            else:
                return r2_score(y_true, y_pred)

    def _is_better_score(self, new_score: float, current_best: float, task_type: str) -> bool:
        """Determine if new score is better than current best"""
        if current_best == float('-inf'):
            return True
        if current_best == float('inf'):
            return True
        return new_score > current_best

    def _calculate_feature_importance(self, model, feature_names: List[str]) -> Dict[str, float]:
        """Calculate feature importance if model supports it"""
        if model is None:
            return {}
        
        try:
            if hasattr(model, 'feature_importances_'):
                importance = model.feature_importances_
            elif hasattr(model, 'coef_'):
                importance = np.abs(model.coef_).flatten()
            else:
                return {}
            
            return dict(zip(feature_names, importance.tolist()))
        except BiologyError as e:
            logger.warning(f"Could not calculate feature importance: {e}")
            return {}

    async def _log_to_mlflow(self, result: Dict, X: pd.DataFrame, y: pd.Series):
        """Log experiment to MLflow"""
        try:
            with mlflow.start_run():
                # Log parameters
                mlflow.log_param("domain", result['domain'])
                mlflow.log_param("task_type", result['task_type'])
                mlflow.log_param("n_samples", len(X))
                mlflow.log_param("n_features", len(X.columns))
                mlflow.log_param("best_framework", result['best_framework'])
                
                # Log metrics
                mlflow.log_metric("best_score", result['best_score'])
                mlflow.log_metric("execution_time", result['execution_time'])
                mlflow.log_metric("models_evaluated", result['models_evaluated'])
                
                # Log model if available
                if result['best_model'] and result['best_model']['model']:
                    mlflow.sklearn.log_model(
                        result['best_model']['model'],
                        "best_model"
                    )
                
        except BiologyError as e:
            logger.warning(f"Failed to log to MLflow: {e}")

    async def process_request(self, request_data: ProcessRequestResult) -> ProcessRequestResult:
        """
        Process a service request - required by BaseService
        """
        try:
            action = request_data.get('action', 'auto_discover_model')
            
            if action == 'auto_discover_model':
                X = request_data.get('X')
                y = request_data.get('y')
                domain = request_data.get('domain', 'general')
                task_type = request_data.get('task_type', 'auto')
                time_limit = request_data.get('time_limit', 300)
                frameworks = request_data.get('frameworks')
                
                if X is None or y is None:
                    return {
                        'success': False,
                        'error': 'X and y data are required'
                    }
                
                result = await self.auto_discover_model(X, y, domain, task_type, time_limit, frameworks)
                result['success'] = True
                return result
            
            else:
                return {
                    'success': False,
                    'error': f'Unknown action: {action}'
                }
                
        except BiologyError as e:
            logger.error(f"Error processing request: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }