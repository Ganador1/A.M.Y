"""
Scikit-Learn Service - Machine Learning Tradicional
Proporciona modelos de clasificación, regresión, clustering y reducción de dimensionalidad
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class ScikitLearnService:
    """Servicio para operaciones de ML tradicional usando scikit-learn"""
    
    def __init__(self):
        self.service_name = "ScikitLearnService"
        logger.info(f"✅ {self.service_name} initialized")
    
    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa solicitudes de operaciones de machine learning
        
        Operaciones soportadas:
        - 'classification' / 'classify': Clasificación con Random Forest
        - 'regression' / 'regress': Regresión con Ridge
        - 'clustering' / 'cluster': Clustering con KMeans
        - 'dimensionality_reduction' / 'reduce_dimensions': Reducción de dimensionalidad con PCA
        - 'cross_validation' / 'cross_validate': Validación cruzada
        - 'feature_selection': Selección de características
        """
        # Soportar tanto 'action' como 'operation' para compatibilidad
        operation = request_data.get('operation') or request_data.get('action')
        
        # Normalizar aliases para retrocompatibilidad
        if operation in ('classify', 'classification'):
            return await self.classification(request_data)
        elif operation in ('regress', 'regression'):
            return await self.regression(request_data)
        elif operation in ('cluster', 'clustering'):
            return await self.clustering(request_data)
        elif operation in ('reduce_dimensions', 'dimensionality_reduction'):
            return await self.dimensionality_reduction(request_data)
        elif operation in ('cross_validate', 'cross_validation'):
            return await self.cross_validation(request_data)
        elif operation == 'feature_selection':
            return await self.feature_selection(request_data)
        else:
            return {
                "success": False,
                "error": f"Unknown operation: {operation}",
                "supported_operations": ['classification', 'regression', 'clustering', 'dimensionality_reduction', 'cross_validation', 'feature_selection']
            }
    
    async def classification(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Clasificación con varios algoritmos"""
        try:
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.model_selection import train_test_split
            from sklearn.datasets import make_classification
            from sklearn.metrics import accuracy_score, f1_score
            import numpy as np
            
            model_type = request_data.get('model', 'random_forest')
            
            # Check for real data input
            X_in = request_data.get('X') or request_data.get('data')
            y_in = request_data.get('y') or request_data.get('target')
            
            if X_in is not None and y_in is not None:
                X = np.array(X_in)
                y = np.array(y_in)
                n_samples, n_features = X.shape
                logger.info(f"Using provided data for classification: {n_samples} samples, {n_features} features")
            else:
                # Fallback to synthetic data
                n_samples = request_data.get('n_samples', 1000)
                n_features = request_data.get('n_features', 20)
                
                # Calcular n_informative y n_redundant dinámicamente
                # Regla: 70% informative, 20% redundant, 10% noise
                n_informative = max(1, int(n_features * 0.7))
                n_redundant = max(0, int(n_features * 0.2))
                # Asegurar que la suma no exceda n_features
                if n_informative + n_redundant > n_features:
                    n_redundant = max(0, n_features - n_informative - 1)
                
                # Generar datos sintéticos
                X, y = make_classification(n_samples=n_samples, n_features=n_features, 
                                          n_informative=n_informative, n_redundant=n_redundant, 
                                          random_state=42)
                logger.info(f"Using synthetic data for classification: {n_samples} samples")
            
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            if model_type == 'random_forest':
                model = RandomForestClassifier(n_estimators=100, random_state=42)
            else:
                model = RandomForestClassifier(n_estimators=100, random_state=42)
            
            # Entrenar
            model.fit(X_train, y_train)
            
            # Predecir
            y_pred = model.predict(X_test)
            
            # Métricas
            accuracy = accuracy_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred, average='weighted')
            
            return {
                "success": True,
                "operation": "classify",
                "model": model_type,
                "training_samples": len(X_train),
                "test_samples": len(X_test),
                "features": int(X.shape[1]),
                "accuracy": float(accuracy),
                "f1_score": float(f1),
                "feature_importances": model.feature_importances_[:10].tolist() if hasattr(model, 'feature_importances_') else []
            }
            
        except Exception as e:
            logger.error(f"Error in classification: {e}")
            return {
                "success": False,
                "error": str(e),
                "operation": "classify"
            }
    
    async def regression(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Regresión lineal y variantes"""
        try:
            from sklearn.linear_model import Ridge
            from sklearn.model_selection import train_test_split
            from sklearn.datasets import make_regression
            from sklearn.metrics import r2_score, mean_squared_error
            import numpy as np
            
            model_type = request_data.get('model', 'ridge')
            
            # Check for real data input
            X_in = request_data.get('X') or request_data.get('data')
            y_in = request_data.get('y') or request_data.get('target')
            
            if X_in is not None and y_in is not None:
                X = np.array(X_in)
                y = np.array(y_in)
                n_samples, n_features = X.shape
                logger.info(f"Using provided data for regression: {n_samples} samples, {n_features} features")
            else:
                n_samples = request_data.get('n_samples', 1000)
                n_features = request_data.get('n_features', 10)
                
                # Generar datos
                X, y = make_regression(n_samples=n_samples, n_features=n_features, 
                                      noise=10.0, random_state=42)
                logger.info(f"Using synthetic data for regression: {n_samples} samples")
            
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Modelo Ridge
            model = Ridge(alpha=1.0)
            model.fit(X_train, y_train)
            
            # Predicciones
            y_pred = model.predict(X_test)
            
            # Métricas
            r2 = r2_score(y_test, y_pred)
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            
            return {
                "success": True,
                "operation": "regress",
                "model": model_type,
                "training_samples": len(X_train),
                "test_samples": len(X_test),
                "features": int(X.shape[1]),
                "r2_score": float(r2),
                "rmse": float(rmse),
                "coefficients": model.coef_[:10].tolist()
            }
            
        except Exception as e:
            logger.error(f"Error in regression: {e}")
            return {
                "success": False,
                "error": str(e),
                "operation": "regress"
            }
    
    async def clustering(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Clustering con KMeans y otros algoritmos"""
        try:
            from sklearn.cluster import KMeans
            from sklearn.datasets import make_blobs
            from sklearn.metrics import silhouette_score
            import numpy as np
            
            n_clusters = request_data.get('n_clusters', 3)
            
            # Check for real data input
            X_in = request_data.get('X') or request_data.get('data')
            
            if X_in is not None:
                X = np.array(X_in)
                n_samples = X.shape[0]
                logger.info(f"Using provided data for clustering: {n_samples} samples")
            else:
                n_samples = request_data.get('n_samples', 500)
                # Generar datos
                # make_blobs returns (X, y)
                blobs = make_blobs(n_samples=n_samples, centers=n_clusters, 
                                n_features=2, random_state=42)
                X = blobs[0]
                logger.info(f"Using synthetic data for clustering: {n_samples} samples")
            
            # KMeans
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            labels = kmeans.fit_predict(X)
            
            # Métricas
            try:
                silhouette = silhouette_score(X, labels)
            except Exception:
                silhouette = 0.0 # Handle case with 1 cluster or error
                
            inertia = kmeans.inertia_
            
            return {
                "success": True,
                "operation": "cluster",
                "algorithm": "kmeans",
                "n_clusters": n_clusters,
                "samples": n_samples,
                "silhouette_score": float(silhouette),
                "inertia": float(inertia),
                "cluster_centers": kmeans.cluster_centers_.tolist(),
                "iterations": int(kmeans.n_iter_)
            }
            
        except Exception as e:
            logger.error(f"Error in clustering: {e}")
            return {
                "success": False,
                "error": str(e),
                "operation": "cluster"
            }
    
    async def dimensionality_reduction(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Reducción de dimensionalidad con PCA"""
        try:
            from sklearn.decomposition import PCA
            from sklearn.datasets import make_classification
            import numpy as np
            
            n_components = request_data.get('n_components', 2)
            
            # Check for real data input
            X_in = request_data.get('X') or request_data.get('data')
            
            if X_in is not None:
                X = np.array(X_in)
                n_samples, n_features = X.shape
                logger.info(f"Using provided data for dimensionality reduction: {n_samples} samples")
            else:
                n_samples = request_data.get('n_samples', 500)
                n_features = request_data.get('n_features', 20)
                
                # Generar datos
                X, _ = make_classification(n_samples=n_samples, n_features=n_features, 
                                          random_state=42)
                logger.info(f"Using synthetic data for dimensionality reduction: {n_samples} samples")
            
            # PCA
            pca = PCA(n_components=n_components)
            X_reduced = pca.fit_transform(X)
            
            # Varianza explicada
            explained_variance = pca.explained_variance_ratio_
            cumulative_variance = np.cumsum(explained_variance)
            
            return {
                "success": True,
                "operation": "reduce_dimensions",
                "method": "PCA",
                "original_dimensions": int(X.shape[1]),
                "reduced_dimensions": n_components,
                "samples": int(X.shape[0]),
                "explained_variance_ratio": explained_variance.tolist(),
                "cumulative_variance": cumulative_variance.tolist(),
                "total_variance_preserved": float(cumulative_variance[-1]),
                "reduced_data": X_reduced.tolist() # Return the reduced data!
            }
            
        except Exception as e:
            logger.error(f"Error in dimensionality reduction: {e}")
            return {
                "success": False,
                "error": str(e),
                "operation": "reduce_dimensions"
            }
    
    async def cross_validation(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validación cruzada"""
        try:
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.model_selection import cross_val_score
            from sklearn.datasets import make_classification
            import numpy as np
            
            cv_folds = request_data.get('cv_folds', 5)
            n_samples = request_data.get('n_samples', 500)
            
            # Generar datos
            X, y = make_classification(n_samples=n_samples, n_features=20, 
                                      random_state=42)
            
            # Modelo
            model = RandomForestClassifier(n_estimators=50, random_state=42)
            
            # Cross-validation
            scores = cross_val_score(model, X, y, cv=cv_folds, scoring='accuracy')
            
            return {
                "success": True,
                "operation": "cross_validate",
                "cv_folds": cv_folds,
                "samples": n_samples,
                "scores": scores.tolist(),
                "mean_score": float(np.mean(scores)),
                "std_score": float(np.std(scores)),
                "min_score": float(np.min(scores)),
                "max_score": float(np.max(scores))
            }
            
        except Exception as e:
            logger.error(f"Error in cross validation: {e}")
            return {
                "success": False,
                "error": str(e),
                "operation": "cross_validate"
            }
    
    async def feature_selection(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Selección de características"""
        try:
            from sklearn.feature_selection import SelectKBest, f_classif
            from sklearn.datasets import make_classification
            import numpy as np
            
            k_features = request_data.get('k_features', 10)
            n_samples = request_data.get('n_samples', 500)
            n_features = request_data.get('n_features', 20)
            
            # Calcular n_informative dinámicamente para evitar errores
            n_informative = min(n_features - 1, max(1, int(n_features * 0.7)))
            
            # Generar datos
            X, y = make_classification(n_samples=n_samples, n_features=n_features, 
                                      n_informative=n_informative, random_state=42)
            
            # Selector
            selector = SelectKBest(score_func=f_classif, k=k_features)
            X_selected = selector.fit_transform(X, y)
            
            # Features seleccionadas
            selected_indices = selector.get_support(indices=True)
            scores = selector.scores_
            
            return {
                "success": True,
                "operation": "feature_selection",
                "method": "SelectKBest",
                "original_features": n_features,
                "selected_features": k_features,
                "selected_indices": selected_indices.tolist(),
                "feature_scores": scores.tolist(),
                "samples": n_samples
            }
            
        except Exception as e:
            logger.error(f"Error in feature selection: {e}")
            return {
                "success": False,
                "error": str(e),
                "operation": "feature_selection"
            }
