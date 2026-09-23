"""
Advanced Scikit-Learn Operations Module for AXIOM

This module provides comprehensive advanced scikit-learn operations, including:
- Advanced supervised and unsupervised learning algorithms
- Model selection and hyperparameter tuning
- Feature engineering and preprocessing pipelines
- Ensemble methods and stacking
- Model evaluation and validation techniques
- Dimensionality reduction and manifold learning
- Clustering algorithms with advanced metrics
- Time series analysis and forecasting
- Anomaly detection and outlier analysis
- Model interpretation and explainability

Author: AXIOM Development Team
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
from sklearn.model_selection import (
    GridSearchCV, RandomizedSearchCV, cross_val_score,
    StratifiedKFold, TimeSeriesSplit, train_test_split
)
from sklearn.preprocessing import (
    StandardScaler, MinMaxScaler, RobustScaler,
    PolynomialFeatures, OneHotEncoder, LabelEncoder, KBinsDiscretizer
)
from sklearn.ensemble import (
    RandomForestClassifier, RandomForestRegressor,
    GradientBoostingClassifier, GradientBoostingRegressor,
    AdaBoostClassifier, AdaBoostRegressor,
    ExtraTreesClassifier, ExtraTreesRegressor,
    VotingClassifier, VotingRegressor, StackingClassifier, StackingRegressor
)
from sklearn.linear_model import (
    LinearRegression, Ridge, Lasso,
    LogisticRegression
)
from sklearn.svm import SVC, SVR
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.cluster import (
    KMeans, DBSCAN, AgglomerativeClustering,
    SpectralClustering, MeanShift, Birch
)
from sklearn.decomposition import PCA, NMF, FastICA, TruncatedSVD
from sklearn.manifold import TSNE, Isomap, LocallyLinearEmbedding, MDS
from sklearn.feature_selection import (
    SelectKBest,
    mutual_info_regression, mutual_info_classif
)
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, mean_squared_error, mean_absolute_error,
    r2_score, silhouette_score, calinski_harabasz_score, davies_bouldin_score
)
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.exceptions import ConvergenceWarning
import warnings
warnings.filterwarnings('ignore', category=ConvergenceWarning)


class AdvancedScikitOperations:
    """
    Advanced scikit-learn operations for comprehensive machine learning workflows.
    """

    def __init__(self):
        """Initialize the advanced scikit-learn operations."""
        self.supervised_algorithms = {
            'classification': {
                'random_forest': RandomForestClassifier(),
                'gradient_boosting': GradientBoostingClassifier(),
                'svm': SVC(),
                'logistic_regression': LogisticRegression(),
                'decision_tree': DecisionTreeClassifier(),
                'naive_bayes': GaussianNB(),
                'knn': KNeighborsClassifier(),
                'adaboost': AdaBoostClassifier(),
                'extra_trees': ExtraTreesClassifier()
            },
            'regression': {
                'random_forest': RandomForestRegressor(),
                'gradient_boosting': GradientBoostingRegressor(),
                'svm': SVR(),
                'linear_regression': LinearRegression(),
                'ridge': Ridge(),
                'lasso': Lasso(),
                'decision_tree': DecisionTreeRegressor(),
                'knn': KNeighborsRegressor(),
                'adaboost': AdaBoostRegressor(),
                'extra_trees': ExtraTreesRegressor()
            }
        }

        self.unsupervised_algorithms = {
            'clustering': {
                'kmeans': KMeans(),
                'dbscan': DBSCAN(),
                'agglomerative': AgglomerativeClustering(),
                'spectral': SpectralClustering(),
                'meanshift': MeanShift(),
                'birch': Birch()
            },
            'dimensionality_reduction': {
                'pca': PCA(),
                'nmf': NMF(),
                'ica': FastICA(),
                'truncated_svd': TruncatedSVD(),
                'tsne': TSNE(),
                'isomap': Isomap(),
                'lle': LocallyLinearEmbedding(),
                'mds': MDS()
            }
        }

    def advanced_ml_pipeline(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive machine learning pipeline with advanced features.

        Args:
            data: Dictionary containing ML data and configuration

        Returns:
            Dictionary with ML pipeline results and metadata
        """
        try:
            # Prepare data
            X, y = self._prepare_ml_data(data)

            # Create preprocessing pipeline
            preprocessor = self._create_preprocessing_pipeline(data)

            # Feature engineering
            if data.get('feature_engineering', False):
                X = self._perform_feature_engineering(X, data)

            # Model selection and training
            model_results = self._perform_model_selection(X, y, data)

            # Hyperparameter tuning
            if data.get('hyperparameter_tuning', False):
                best_model = self._perform_hyperparameter_tuning(X, y, data)
                model_results['best_model'] = best_model

            # Model evaluation
            evaluation = self._comprehensive_model_evaluation(X, y, model_results, data)

            # Feature importance analysis
            if data.get('feature_importance', False):
                feature_importance = self._analyze_feature_importance(X, y, data)
                evaluation['feature_importance'] = feature_importance

            return {
                'data_info': {
                    'n_samples': X.shape[0],
                    'n_features': X.shape[1],
                    'target_type': 'classification' if data.get('task_type') == 'classification' else 'regression'
                },
                'preprocessing': preprocessor,
                'model_results': model_results,
                'evaluation': evaluation,
                'pipeline_metadata': {
                    'feature_engineering_applied': data.get('feature_engineering', False),
                    'hyperparameter_tuning_performed': data.get('hyperparameter_tuning', False),
                    'feature_importance_analyzed': data.get('feature_importance', False)
                }
            }

        except Exception as e:
            return {'error': f'Advanced ML pipeline failed: {str(e)}'}

    def _prepare_ml_data(self, data: Dict[str, Any]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare data for machine learning."""
        if 'X' in data and 'y' in data:
            X = np.array(data['X'])
            y = np.array(data['y'])
        elif 'dataframe' in data:
            df = data['dataframe']
            target_column = data.get('target_column', df.columns[-1])
            X = df.drop(columns=[target_column]).values
            y = df[target_column].values
        else:
            raise ValueError("Data must contain 'X' and 'y' arrays or 'dataframe' with 'target_column'")

        return X, y

    def _create_preprocessing_pipeline(self, data: Dict[str, Any]) -> Pipeline:
        """Create comprehensive preprocessing pipeline."""
        steps = []

        # Handle missing values
        if data.get('handle_missing', True):
            imputer = self._create_imputer(data)
            steps.append(('imputer', imputer))

        # Feature scaling
        if data.get('scaling', 'standard') != 'none':
            scaler = self._create_scaler(data)
            steps.append(('scaler', scaler))

        # Categorical encoding
        if data.get('categorical_features'):
            encoder = self._create_encoder(data)
            steps.append(('encoder', encoder))

        return Pipeline(steps)

    def _create_imputer(self, data: Dict[str, Any]):
        """Create appropriate imputer based on data characteristics."""
        strategy = data.get('imputation_strategy', 'mean')

        if strategy == 'knn':
            return KNNImputer(n_neighbors=data.get('knn_neighbors', 5))
        else:
            return SimpleImputer(strategy=strategy)

    def _create_scaler(self, data: Dict[str, Any]):
        """Create appropriate scaler."""
        scaling_type = data.get('scaling', 'standard')

        if scaling_type == 'minmax':
            return MinMaxScaler()
        elif scaling_type == 'robust':
            return RobustScaler()
        else:
            return StandardScaler()

    def _create_encoder(self, data: Dict[str, Any]):
        """Create categorical encoder."""
        if data.get('encoding_type', 'onehot') == 'label':
            return LabelEncoder()
        else:
            return OneHotEncoder(handle_unknown='ignore', sparse=False)

    def _perform_feature_engineering(self, X: np.ndarray, data: Dict[str, Any]) -> np.ndarray:
        """Perform advanced feature engineering."""
        engineered_features = [X]

        # Polynomial features
        if data.get('polynomial_features', False):
            degree = data.get('polynomial_degree', 2)
            poly = PolynomialFeatures(degree=degree, include_bias=False)
            poly_features = poly.fit_transform(X)
            engineered_features.append(poly_features)

        # Interaction features
        if data.get('interaction_features', False):
            interaction = PolynomialFeatures(degree=2, interaction_only=True, include_bias=False)
            interaction_features = interaction.fit_transform(X)
            engineered_features.append(interaction_features)

        # Binning features
        if data.get('binning_features', False):
            n_bins = data.get('n_bins', 5)
            binner = KBinsDiscretizer(n_bins=n_bins, encode='ordinal', strategy='quantile')
            binned_features = binner.fit_transform(X)
            engineered_features.append(binned_features)

        return np.concatenate(engineered_features, axis=1)

    def _perform_model_selection(self, X: np.ndarray, y: np.ndarray, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform model selection with multiple algorithms."""
        task_type = data.get('task_type', 'classification')
        algorithms = self.supervised_algorithms[task_type]

        results = {}
        cv_scores = {}

        # Cross-validation strategy
        cv = self._create_cv_strategy(data)

        for name, model in algorithms.items():
            try:
                # Train and evaluate model
                scores = cross_val_score(model, X, y, cv=cv, scoring=self._get_scoring_metric(task_type))
                cv_scores[name] = {
                    'mean_score': np.mean(scores),
                    'std_score': np.std(scores),
                    'scores': scores.tolist()
                }

                # Fit model on full training data
                model.fit(X, y)
                results[name] = model

            except Exception as e:
                cv_scores[name] = {'error': str(e)}

        # Select best model
        best_model_name = max(cv_scores.keys(),
                           key=lambda x: cv_scores[x].get('mean_score', -np.inf) if isinstance(cv_scores[x], dict) else -np.inf)

        return {
            'models': results,
            'cv_scores': cv_scores,
            'best_model_name': best_model_name,
            'best_score': cv_scores[best_model_name].get('mean_score', 'N/A')
        }

    def _create_cv_strategy(self, data: Dict[str, Any]):
        """Create appropriate cross-validation strategy."""
        cv_type = data.get('cv_type', 'stratified')

        if cv_type == 'timeseries':
            return TimeSeriesSplit(n_splits=data.get('n_splits', 5))
        elif cv_type == 'stratified':
            return StratifiedKFold(n_splits=data.get('n_splits', 5), shuffle=True, random_state=42)
        else:
            from sklearn.model_selection import KFold
            return KFold(n_splits=data.get('n_splits', 5), shuffle=True, random_state=42)

    def _get_scoring_metric(self, task_type: str) -> str:
        """Get appropriate scoring metric."""
        if task_type == 'classification':
            return 'accuracy'
        else:
            return 'neg_mean_squared_error'

    def _perform_hyperparameter_tuning(self, X: np.ndarray, y: np.ndarray, data: Dict[str, Any]):
        """Perform hyperparameter tuning using grid or random search."""
        task_type = data.get('task_type', 'classification')
        model_name = data.get('model_for_tuning', 'random_forest')

        if model_name not in self.supervised_algorithms[task_type]:
            raise ValueError(f"Model {model_name} not found for task type {task_type}")

        model = self.supervised_algorithms[task_type][model_name]

        # Get parameter grid
        param_grid = self._get_parameter_grid(model_name, task_type)

        # Choose search method
        search_method = data.get('search_method', 'grid')
        cv = self._create_cv_strategy(data)

        if search_method == 'random':
            search = RandomizedSearchCV(
                model, param_grid, n_iter=data.get('n_iter', 50),
                cv=cv, scoring=self._get_scoring_metric(task_type),
                random_state=42, n_jobs=-1
            )
        else:
            search = GridSearchCV(
                model, param_grid, cv=cv,
                scoring=self._get_scoring_metric(task_type), n_jobs=-1
            )

        search.fit(X, y)

        return {
            'best_estimator': search.best_estimator_,
            'best_params': search.best_params_,
            'best_score': search.best_score_,
            'cv_results': search.cv_results_
        }

    def _get_parameter_grid(self, model_name: str, task_type: str) -> Dict[str, Any]:
        """Get parameter grid for hyperparameter tuning."""
        if model_name == 'random_forest':
            if task_type == 'classification':
                return {
                    'n_estimators': [100, 200, 300],
                    'max_depth': [10, 20, None],
                    'min_samples_split': [2, 5, 10],
                    'min_samples_leaf': [1, 2, 4],
                    'max_features': ['sqrt', 'log2']
                }
            else:
                return {
                    'n_estimators': [100, 200, 300],
                    'max_depth': [10, 20, None],
                    'min_samples_split': [2, 5, 10],
                    'min_samples_leaf': [1, 2, 4],
                    'max_features': ['auto', 'sqrt']
                }
        elif model_name == 'svm':
            return {
                'C': [0.1, 1, 10, 100],
                'kernel': ['linear', 'rbf', 'poly'],
                'gamma': ['scale', 'auto', 0.001, 0.01, 0.1, 1]
            }
        elif model_name == 'gradient_boosting':
            return {
                'n_estimators': [100, 200, 300],
                'learning_rate': [0.01, 0.1, 0.2],
                'max_depth': [3, 5, 7],
                'min_samples_split': [2, 5, 10]
            }
        else:
            return {}  # Default empty grid

    def _comprehensive_model_evaluation(self, X: np.ndarray, y: np.ndarray,
                                      model_results: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive model evaluation."""
        evaluation = {}

        # Split data for evaluation
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=data.get('test_size', 0.2), random_state=42
        )

        task_type = data.get('task_type', 'classification')

        for model_name, model in model_results.get('models', {}).items():
            try:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)

                if task_type == 'classification':
                    evaluation[model_name] = {
                        'accuracy': accuracy_score(y_test, y_pred),
                        'precision': precision_score(y_test, y_pred, average='weighted'),
                        'recall': recall_score(y_test, y_pred, average='weighted'),
                        'f1_score': f1_score(y_test, y_pred, average='weighted')
                    }

                    # ROC-AUC for binary classification
                    if len(np.unique(y)) == 2:
                        y_pred_proba = model.predict_proba(X_test)[:, 1]
                        evaluation[model_name]['roc_auc'] = roc_auc_score(y_test, y_pred_proba)

                else:  # regression
                    evaluation[model_name] = {
                        'mse': mean_squared_error(y_test, y_pred),
                        'mae': mean_absolute_error(y_test, y_pred),
                        'r2_score': r2_score(y_test, y_pred),
                        'rmse': np.sqrt(mean_squared_error(y_test, y_pred))
                    }

            except Exception as e:
                evaluation[model_name] = {'error': str(e)}

        return evaluation

    def _analyze_feature_importance(self, X: np.ndarray, y: np.ndarray, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze feature importance using various methods."""
        importance_results = {}

        # Tree-based feature importance
        rf = RandomForestClassifier(random_state=42) if data.get('task_type') == 'classification' else RandomForestRegressor(random_state=42)
        rf.fit(X, y)
        importance_results['random_forest'] = rf.feature_importances_

        # Permutation importance
        from sklearn.inspection import permutation_importance
        perm_importance = permutation_importance(rf, X, y, n_repeats=10, random_state=42)
        importance_results['permutation'] = perm_importance.importances_mean

        # Mutual information
        if data.get('task_type') == 'classification':
            mi_scores = mutual_info_classif(X, y)
        else:
            mi_scores = mutual_info_regression(X, y)
        importance_results['mutual_info'] = mi_scores

        # Feature selection
        if data.get('feature_selection', False):
            selector = SelectKBest(score_func=mutual_info_classif if data.get('task_type') == 'classification' else mutual_info_regression,
                                  k=data.get('k_features', 'all'))
            selector.fit(X, y)
            importance_results['selected_features'] = selector.get_support(indices=True)

        return importance_results

    def advanced_clustering_pipeline(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Advanced clustering pipeline with multiple algorithms and evaluation.

        Args:
            data: Dictionary containing clustering data and configuration

        Returns:
            Dictionary with clustering results and evaluation metrics
        """
        try:
            X = np.array(data['X'])

            # Preprocessing
            if data.get('preprocessing', True):
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X)
            else:
                X_scaled = X

            clustering_results = {}

            # Apply multiple clustering algorithms
            algorithms = data.get('algorithms', ['kmeans', 'dbscan', 'agglomerative'])

            for algorithm in algorithms:
                if algorithm in self.unsupervised_algorithms['clustering']:
                    result = self._apply_clustering_algorithm(X_scaled, algorithm, data)
                    clustering_results[algorithm] = result

            # Evaluate clustering quality
            evaluation = self._evaluate_clustering_quality(X_scaled, clustering_results, data)

            # Visualize clusters if requested
            if data.get('visualize', False):
                visualization = self._visualize_clusters(X_scaled, clustering_results, data)
                evaluation['visualization'] = visualization

            return {
                'data_info': {
                    'n_samples': X.shape[0],
                    'n_features': X.shape[1]
                },
                'clustering_results': clustering_results,
                'evaluation': evaluation,
                'preprocessing_applied': data.get('preprocessing', True)
            }

        except Exception as e:
            return {'error': f'Advanced clustering pipeline failed: {str(e)}'}

    def _apply_clustering_algorithm(self, X: np.ndarray, algorithm: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply specific clustering algorithm."""
        model = self.unsupervised_algorithms['clustering'][algorithm]

        # Set algorithm-specific parameters
        if algorithm == 'kmeans':
            model.set_params(n_clusters=data.get('n_clusters', 3), random_state=42)
        elif algorithm == 'dbscan':
            model.set_params(eps=data.get('eps', 0.5), min_samples=data.get('min_samples', 5))
        elif algorithm == 'agglomerative':
            model.set_params(n_clusters=data.get('n_clusters', 3))

        try:
            labels = model.fit_predict(X)

            return {
                'labels': labels.tolist(),
                'n_clusters': len(np.unique(labels[labels != -1])),  # Exclude noise points
                'model': model,
                'cluster_centers': model.cluster_centers_.tolist() if hasattr(model, 'cluster_centers_') else None
            }

        except Exception as e:
            return {'error': str(e)}

    def _evaluate_clustering_quality(self, X: np.ndarray, clustering_results: Dict[str, Any],
                                   data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate clustering quality using multiple metrics."""
        evaluation = {}

        for algorithm, result in clustering_results.items():
            if 'error' not in result:
                labels = np.array(result['labels'])

                # Skip evaluation if only one cluster or all noise
                if len(np.unique(labels[labels != -1])) <= 1:
                    evaluation[algorithm] = {'warning': 'Insufficient clusters for evaluation'}
                    continue

                try:
                    # Silhouette score
                    if len(np.unique(labels[labels != -1])) > 1:
                        silhouette = silhouette_score(X, labels)
                    else:
                        silhouette = 'N/A'

                    # Calinski-Harabasz score
                    if len(np.unique(labels[labels != -1])) > 1:
                        ch_score = calinski_harabasz_score(X, labels)
                    else:
                        ch_score = 'N/A'

                    # Davies-Bouldin score
                    if len(np.unique(labels[labels != -1])) > 1:
                        db_score = davies_bouldin_score(X, labels)
                    else:
                        db_score = 'N/A'

                    evaluation[algorithm] = {
                        'silhouette_score': silhouette,
                        'calinski_harabasz_score': ch_score,
                        'davies_bouldin_score': db_score,
                        'n_clusters_found': result['n_clusters']
                    }

                except Exception as e:
                    evaluation[algorithm] = {'error': str(e)}

        return evaluation

    def _visualize_clusters(self, X: np.ndarray, clustering_results: Dict[str, Any],
                          data: Dict[str, Any]) -> Dict[str, Any]:
        """Create cluster visualizations."""
        visualization = {}

        try:
            import matplotlib.pyplot as plt

            # Reduce dimensionality for visualization if needed
            if X.shape[1] > 2:
                pca = PCA(n_components=2, random_state=42)
                X_vis = pca.fit_transform(X)
                visualization['dimensionality_reduction'] = 'PCA'
            else:
                X_vis = X

            # Create subplots for each algorithm
            n_algorithms = len(clustering_results)
            fig, axes = plt.subplots(1, n_algorithms, figsize=(6*n_algorithms, 5))

            if n_algorithms == 1:
                axes = [axes]

            for i, (algorithm, result) in enumerate(clustering_results.items()):
                if 'error' not in result:
                    labels = np.array(result['labels'])
                    scatter = axes[i].scatter(X_vis[:, 0], X_vis[:, 1], c=labels, cmap='viridis', alpha=0.6)
                    axes[i].set_title(f'{algorithm.upper()} Clustering')
                    axes[i].set_xlabel('Component 1')
                    axes[i].set_ylabel('Component 2')
                    plt.colorbar(scatter, ax=axes[i])

            plt.tight_layout()
            visualization['figure'] = fig
            visualization['n_plots'] = n_algorithms

        except Exception as e:
            visualization['error'] = f'Visualization failed: {str(e)}'

        return visualization

    def ensemble_methods_pipeline(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Advanced ensemble methods pipeline with stacking and voting.

        Args:
            data: Dictionary containing ensemble data and configuration

        Returns:
            Dictionary with ensemble results and comparison
        """
        try:
            X, y = self._prepare_ml_data(data)
            task_type = data.get('task_type', 'classification')

            # Base estimators
            base_estimators = self._create_base_estimators(task_type, data)

            ensemble_results = {}

            # Voting ensemble
            if data.get('voting_ensemble', True):
                voting = self._create_voting_ensemble(base_estimators, task_type)
                ensemble_results['voting'] = self._evaluate_ensemble(voting, X, y, data)

            # Stacking ensemble
            if data.get('stacking_ensemble', True):
                stacking = self._create_stacking_ensemble(base_estimators, task_type, data)
                ensemble_results['stacking'] = self._evaluate_ensemble(stacking, X, y, data)

            # Compare with individual models
            individual_results = self._evaluate_individual_models(base_estimators, X, y, data)
            ensemble_results['individual_comparison'] = individual_results

            return {
                'ensemble_results': ensemble_results,
                'base_estimators': [name for name, _ in base_estimators],
                'task_type': task_type,
                'data_info': {
                    'n_samples': X.shape[0],
                    'n_features': X.shape[1]
                }
            }

        except Exception as e:
            return {'error': f'Ensemble methods pipeline failed: {str(e)}'}

    def _create_base_estimators(self, task_type: str, data: Dict[str, Any]) -> List[Tuple[str, Any]]:
        """Create base estimators for ensemble."""
        base_models = data.get('base_models', ['random_forest', 'gradient_boosting', 'svm'])

        estimators = []
        for model_name in base_models:
            if model_name in self.supervised_algorithms[task_type]:
                model = self.supervised_algorithms[task_type][model_name]
                estimators.append((model_name, model))

        return estimators

    def _create_voting_ensemble(self, base_estimators: List[Tuple[str, Any]], task_type: str):
        """Create voting ensemble."""
        if task_type == 'classification':
            return VotingClassifier(estimators=base_estimators, voting='soft')
        else:
            return VotingRegressor(estimators=base_estimators)

    def _create_stacking_ensemble(self, base_estimators: List[Tuple[str, Any]], task_type: str, data: Dict[str, Any]):
        """Create stacking ensemble."""
        final_estimator = data.get('final_estimator', 'logistic_regression' if task_type == 'classification' else 'linear_regression')

        if task_type == 'classification':
            final_est = self.supervised_algorithms[task_type][final_estimator]
            return StackingClassifier(estimators=base_estimators, final_estimator=final_est, cv=5)
        else:
            final_est = self.supervised_algorithms[task_type][final_estimator]
            return StackingRegressor(estimators=base_estimators, final_estimator=final_est, cv=5)

    def _evaluate_ensemble(self, ensemble_model, X: np.ndarray, y: np.ndarray, data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate ensemble model performance."""
        try:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            ensemble_model.fit(X_train, y_train)
            y_pred = ensemble_model.predict(X_test)

            task_type = data.get('task_type', 'classification')

            if task_type == 'classification':
                return {
                    'accuracy': accuracy_score(y_test, y_pred),
                    'precision': precision_score(y_test, y_pred, average='weighted'),
                    'recall': recall_score(y_test, y_pred, average='weighted'),
                    'f1_score': f1_score(y_test, y_pred, average='weighted')
                }
            else:
                return {
                    'mse': mean_squared_error(y_test, y_pred),
                    'mae': mean_absolute_error(y_test, y_pred),
                    'r2_score': r2_score(y_test, y_pred)
                }

        except Exception as e:
            return {'error': str(e)}

    def _evaluate_individual_models(self, base_estimators: List[Tuple[str, Any]],
                                  X: np.ndarray, y: np.ndarray, data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate individual base models for comparison."""
        results = {}

        for name, model in base_estimators:
            results[name] = self._evaluate_ensemble(model, X, y, data)

        return results

    def anomaly_detection_pipeline(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Advanced anomaly detection pipeline.

        Args:
            data: Dictionary containing anomaly detection data and configuration

        Returns:
            Dictionary with anomaly detection results
        """
        try:
            X = np.array(data['X'])

            anomaly_results = {}

            # Isolation Forest
            from sklearn.ensemble import IsolationForest
            iso_forest = IsolationForest(contamination=data.get('contamination', 0.1), random_state=42)
            anomaly_results['isolation_forest'] = {
                'scores': iso_forest.fit_predict(X).tolist(),
                'anomaly_scores': (-iso_forest.score_samples(X)).tolist()
            }

            # Local Outlier Factor
            from sklearn.neighbors import LocalOutlierFactor
            lof = LocalOutlierFactor(contamination=data.get('contamination', 0.1))
            anomaly_results['local_outlier_factor'] = {
                'scores': lof.fit_predict(X).tolist(),
                'anomaly_scores': (-lof.negative_outlier_factor_).tolist()
            }

            # One-Class SVM
            from sklearn.svm import OneClassSVM
            ocsvm = OneClassSVM(nu=data.get('contamination', 0.1))
            anomaly_results['one_class_svm'] = {
                'scores': ocsvm.fit_predict(X).tolist()
            }

            return {
                'anomaly_results': anomaly_results,
                'contamination_level': data.get('contamination', 0.1),
                'data_info': {
                    'n_samples': X.shape[0],
                    'n_features': X.shape[1]
                }
            }

        except Exception as e:
            return {'error': f'Anomaly detection pipeline failed: {str(e)}'}
