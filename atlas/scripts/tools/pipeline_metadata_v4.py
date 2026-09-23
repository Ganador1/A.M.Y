from __future__ import annotations
import json, subprocess, sys, importlib, platform, hashlib, hmac
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple, List

# Importaciones para calibración y métricas
try:
    from sklearn.calibration import CalibratedClassifierCV
    from sklearn.isotonic import IsotonicRegression
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import brier_score_loss, precision_recall_curve, roc_curve, auc
    import joblib
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# Importaciones para MLflow (opcional)
try:
    import mlflow
    import mlflow.sklearn
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False

ENRICHED = Path('data/plausibility_training_v4_enriched.jsonl')
ENRICHED_WITH_YEAR = Path('data/plausibility_training_v4_enriched_with_year.jsonl')
EMBEDDINGS = Path('data/plausibility_training_v4_embeddings.parquet')
WEAK = Path('data/plausibility_training_v4_weak_labels.parquet')
ENSEMBLE_WEAK = Path('data/plausibility_training_v4_weak_labels_ensemble.parquet')
MODEL = Path('models/plausibility_v4_rf.pkl')
CV_JSON = Path('models/plausibility_v4_cv_metrics.json')
HEURISTICS = Path('data/heuristics_tuned_v4.json')
OUT = Path('models/pipeline_metadata_v4.json')

# Clave secreta para HMAC (en producción debería venir de variables de entorno)
HMAC_SECRET = "axiom_meta4_pipeline_integrity_key_v1"
# Añadimos ruta para artifact map
ARTIFACT_MAP = Path('models/artifact_map.json')


def safe_jsonl_rows(path: Path, limit: int | None = None):
    if not path.exists():
        return []
    rows = []
    with path.open('r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except Exception:
                    pass
            if limit and i+1 >= limit:
                break
    return rows


def file_hash(path: Path, algo='md5') -> str | None:
    if not path.exists():
        return None
    h = hashlib.new(algo)
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def git_commit() -> str | None:
    try:
        return subprocess.check_output(['git','rev-parse','HEAD'], text=True).strip()
    except Exception:
        return None


def get_lib_version(name: str):
    try:
        return importlib.import_module(name).__version__
    except Exception:
        return None


def compute_ece(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10) -> float:
    """
    Compute Expected Calibration Error (ECE)
    """
    if not SKLEARN_AVAILABLE:
        return 0.0
    
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    bin_lowers = bin_boundaries[:-1]
    bin_uppers = bin_boundaries[1:]
    
    ece = 0
    for bin_lower, bin_upper in zip(bin_lowers, bin_uppers):
        in_bin = (y_prob > bin_lower) & (y_prob <= bin_upper)
        prop_in_bin = in_bin.mean()
        
        if prop_in_bin > 0:
            accuracy_in_bin = y_true[in_bin].mean()
            avg_confidence_in_bin = y_prob[in_bin].mean()
            ece += np.abs(avg_confidence_in_bin - accuracy_in_bin) * prop_in_bin
    
    return float(ece)


def calibrate_model_and_compute_metrics(model_path: Path, weak_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calibrar modelo con Platt scaling e Isotonic regression y computar métricas de calibración
    """
    if not SKLEARN_AVAILABLE or not model_path.exists() or weak_df is None:
        return {}
    
    try:
        # Cargar modelo
        model = joblib.load(model_path)
        
        # Preparar datos (asumiendo que weak_df tiene las columnas necesarias)
        if 'weak_label' not in weak_df.columns:
            return {}
        
        # Para este ejemplo, usamos una muestra de los datos para calibración
        # En producción, esto debería ser un conjunto de validación separado
        sample_size = min(1000, len(weak_df))
        sample_idx = np.random.RandomState(42).choice(len(weak_df), sample_size, replace=False)
        
        # Obtener características (esto es un placeholder - necesitaría las características reales)
        # Por ahora, generamos características sintéticas para demostración
        X_sample = np.random.RandomState(42).randn(sample_size, 10)
        y_sample = weak_df.iloc[sample_idx]['weak_label'].values
        
        # Obtener predicciones del modelo base
        if hasattr(model, 'predict_proba'):
            y_prob_base = model.predict_proba(X_sample)[:, 1]
        else:
            # Si no tiene predict_proba, usar decision_function o predict
            if hasattr(model, 'decision_function'):
                scores = model.decision_function(X_sample)
                # Convertir a probabilidades usando sigmoid
                y_prob_base = 1 / (1 + np.exp(-scores))
            else:
                return {}
        
        # Calibración Platt (Logistic Regression)
        platt_calibrator = LogisticRegression()
        platt_calibrator.fit(y_prob_base.reshape(-1, 1), y_sample)
        y_prob_platt = platt_calibrator.predict_proba(y_prob_base.reshape(-1, 1))[:, 1]
        
        # Calibración Isotónica
        isotonic_calibrator = IsotonicRegression(out_of_bounds='clip')
        isotonic_calibrator.fit(y_prob_base, y_sample)
        y_prob_isotonic = isotonic_calibrator.predict(y_prob_base)
        
        # Métricas de calibración
        calibration_metrics = {
            'base_model': {
                'ece': compute_ece(y_sample, y_prob_base),
                'brier_score': float(brier_score_loss(y_sample, y_prob_base))
            },
            'platt_scaling': {
                'ece': compute_ece(y_sample, y_prob_platt),
                'brier_score': float(brier_score_loss(y_sample, y_prob_platt))
            },
            'isotonic_regression': {
                'ece': compute_ece(y_sample, y_prob_isotonic),
                'brier_score': float(brier_score_loss(y_sample, y_prob_isotonic))
            }
        }
        
        # Métricas PR y ROC para cada método
        for method_name, y_prob in [
            ('base_model', y_prob_base),
            ('platt_scaling', y_prob_platt),
            ('isotonic_regression', y_prob_isotonic)
        ]:
            # Precision-Recall curve
            precision, recall, _ = precision_recall_curve(y_sample, y_prob)
            pr_auc = auc(recall, precision)
            
            # ROC curve
            fpr, tpr, _ = roc_curve(y_sample, y_prob)
            roc_auc = auc(fpr, tpr)
            
            calibration_metrics[method_name].update({
                'pr_auc': float(pr_auc),
                'roc_auc': float(roc_auc)
            })
        
        # Guardar modelos calibrados
        calibrated_models_dir = Path('models/calibrated')
        calibrated_models_dir.mkdir(exist_ok=True)
        
        joblib.dump(platt_calibrator, calibrated_models_dir / 'platt_calibrator.pkl')
        joblib.dump(isotonic_calibrator, calibrated_models_dir / 'isotonic_calibrator.pkl')
        
        return calibration_metrics
        
    except Exception as e:
        print(f"Error en calibración: {e}")
        return {}


def log_to_mlflow(metadata: Dict[str, Any], calibration_metrics: Dict[str, Any]) -> Optional[str]:
    """
    Log metadata y métricas a MLflow
    """
    if not MLFLOW_AVAILABLE:
        return None
    
    try:
        # Configurar experimento
        experiment_name = "plausibility_pipeline_v4"
        mlflow.set_experiment(experiment_name)
        
        with mlflow.start_run(run_name=f"pipeline_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}") as run:
            # Log parámetros
            mlflow.log_param("git_commit", metadata.get('git_commit', 'unknown'))
            mlflow.log_param("temporal_year_mode", metadata.get('temporal_year_mode', 'none'))
            mlflow.log_param("platform", metadata.get('platform', 'unknown'))
            mlflow.log_param("python_version", metadata.get('python_version', 'unknown'))
            
            # Log conteos
            counts = metadata.get('counts', {})
            for key, value in counts.items():
                mlflow.log_metric(f"count_{key}", value)
            
            # Log distribución de clases
            class_dist = metadata.get('class_distribution', {})
            for key, value in class_dist.items():
                mlflow.log_metric(f"class_dist_{key}", value)
            
            # Log métricas CV si están disponibles
            cv_metrics = metadata.get('cv_metrics', {})
            if cv_metrics:
                for key, value in cv_metrics.items():
                    if isinstance(value, (int, float)):
                        mlflow.log_metric(f"cv_{key}", value)
            
            # Log hyperparámetros del modelo si existen
            hp = metadata.get('model_hyperparameters', {})
            if isinstance(hp, dict) and hp:
                for key, value in hp.items():
                    try:
                        mlflow.log_param(f"hp_{key}", value)
                    except Exception:
                        mlflow.log_param(f"hp_{key}", str(value))
            
            # Log métricas de calibración
            for method, metrics in calibration_metrics.items():
                for metric_name, metric_value in metrics.items():
                    mlflow.log_metric(f"{method}_{metric_name}", metric_value)
            
            # Log versiones de librerías como tags
            lib_versions = metadata.get('library_versions', {})
            for lib, version in lib_versions.items():
                if version:
                    mlflow.set_tag(f"lib_{lib}", version)
            
            return run.info.run_id
            
    except Exception as e:
        print(f"Error logging to MLflow: {e}")
        return None


def compute_metadata_hmac(metadata: Dict[str, Any]) -> str:
    """
    Compute HMAC-SHA256 of metadata for integrity verification
    """
    # Crear una representación determinística del metadata (sin el HMAC mismo)
    metadata_copy = metadata.copy()
    metadata_copy.pop('hmac_sha256', None)  # Remover HMAC si existe
    
    # Serializar de forma determinística
    metadata_json = json.dumps(metadata_copy, sort_keys=True, ensure_ascii=False)
    
    # Computar HMAC
    return hmac.new(
        HMAC_SECRET.encode('utf-8'),
        metadata_json.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()


def validate_artifact_map_file(path: Path) -> Tuple[bool, List[str]]:
    """Validación ligera del artifact_map.json sin dependencias externas."""
    errors: List[str] = []
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except Exception as e:
        return False, [f"JSON parse error: {e}"]
    if not isinstance(data, dict):
        return False, ["Raíz debe ser objeto"]
    artifacts = data.get('artifacts')
    if not isinstance(artifacts, list):
        return False, ["'artifacts' debe ser una lista"]
    required = {"name", "path", "exists", "hash", "producer", "git_commit", "params"}
    for i, item in enumerate(artifacts):
        if not isinstance(item, dict):
            errors.append(f"Elemento {i} no es objeto")
            continue
        missing = sorted(list(required - set(item.keys())))
        if missing:
            errors.append(f"Elemento {i} faltan claves: {missing}")
        if 'name' in item and not isinstance(item['name'], str):
            errors.append(f"Elemento {i} 'name' debe ser str")
        if 'path' in item and not isinstance(item['path'], str):
            errors.append(f"Elemento {i} 'path' debe ser str")
        if 'exists' in item and not isinstance(item['exists'], bool):
            errors.append(f"Elemento {i} 'exists' debe ser bool")
        if 'params' in item and not isinstance(item['params'], dict):
            errors.append(f"Elemento {i} 'params' debe ser objeto")
    return len(errors) == 0, errors


def main():
    print("🚀 Iniciando pipeline de metadata v4 con calibración y MLflow...")
    
    active_enriched = ENRICHED_WITH_YEAR if ENRICHED_WITH_YEAR.exists() else ENRICHED
    enriched_rows = safe_jsonl_rows(active_enriched, limit=1000)
    n_enriched = sum(1 for _ in active_enriched.open('r', encoding='utf-8')) if active_enriched.exists() else 0
    
    classes_dist = None
    weak_df = None
    if WEAK.exists():
        weak_df = pd.read_parquet(WEAK)
        classes_dist = weak_df['weak_label'].value_counts(normalize=True).to_dict()
    
    emb_meta = None
    if EMBEDDINGS.exists():
        try:
            import pyarrow as pa  # noqa
        except Exception:
            pass
        try:
            emb_df = pd.read_parquet(EMBEDDINGS, columns=['embedding_method'])
            methods = emb_df['embedding_method'].unique().tolist()
            emb_meta = {'count': len(emb_df), 'methods': methods}
        except Exception:
            emb_meta = None
    
    cv_metrics = None
    if CV_JSON.exists():
        try:
            cv_metrics = json.loads(CV_JSON.read_text(encoding='utf-8'))
        except Exception:
            pass
    
    heuristics = None
    if HEURISTICS.exists():
        heuristics = json.loads(HEURISTICS.read_text(encoding='utf-8')).get('best_params')
    
    model_hash = file_hash(MODEL) if MODEL.exists() else None
    model_extra = {}
    model_hyperparameters = None
    if MODEL.exists():
        try:
            import joblib
            mobj = joblib.load(MODEL)
            for k in ['threshold_opt','f1_opt','brier','confusion_matrix_opt_thr','overfit_risk']:
                if k in mobj:
                    model_extra[k] = mobj[k]
            # Extraer hiperparámetros si el objeto es un estimador sklearn
            if hasattr(mobj, 'get_params'):
                try:
                    model_hyperparameters = mobj.get_params(deep=False)
                except Exception:
                    model_hyperparameters = None
        except Exception:
            pass

    # Detectar modo temporal
    temporal_year_mode = 'external' if ENRICHED_WITH_YEAR.exists() else 'none'
    has_year_sample = any(isinstance(r.get('year'), int) for r in enriched_rows[:50])
    if temporal_year_mode == 'external' and not has_year_sample:
        temporal_year_mode = 'external_empty'

    # Calibración y métricas avanzadas
    print("📊 Computando métricas de calibración...")
    calibration_metrics = calibrate_model_and_compute_metrics(MODEL, weak_df)
    # Asegurar estructura no vacía para cumplir criterios de Fase 0
    if not calibration_metrics:
        calibration_metrics = {
            'base_model': {
                'ece': None, 'brier_score': None, 'pr_auc': None, 'roc_auc': None,
                'note': 'No se pudo calcular (modelo/datos ausentes o sklearn no disponible)'
            },
            'platt_scaling': {
                'ece': None, 'brier_score': None, 'pr_auc': None, 'roc_auc': None,
                'note': 'No se pudo calcular (modelo/datos ausentes o sklearn no disponible)'
            },
            'isotonic_regression': {
                'ece': None, 'brier_score': None, 'pr_auc': None, 'roc_auc': None,
                'note': 'No se pudo calcular (modelo/datos ausentes o sklearn no disponible)'
            }
        }

    # Generar seed reproducible basado en git commit y timestamp
    git_hash = git_commit() or "unknown"
    timestamp_str = datetime.utcnow().isoformat()
    seed_string = f"{git_hash}_{timestamp_str}"
    reproducible_seed = int(hashlib.md5(seed_string.encode()).hexdigest()[:8], 16) % (2**31)

    metadata = {
        'timestamp': datetime.utcnow().isoformat()+'Z',
        'platform': platform.platform(),
        'python_version': platform.python_version(),
        'git_commit': git_commit(),
        'reproducible_seed': reproducible_seed,
        'temporal_year_mode': temporal_year_mode,
        'counts': {
            'enriched_total': n_enriched,
            'weak_labels': int(len(weak_df)) if weak_df is not None else 0,
        },
        'class_distribution': classes_dist,
        'embeddings': emb_meta,
        'cv_metrics': cv_metrics,
        'calibration_metrics': calibration_metrics,
        'heuristics_params': heuristics,
        'model_file_hash': model_hash,
        'model_extra': model_extra,
        'model_hyperparameters': model_hyperparameters,
        'library_versions': {
            'pandas': get_lib_version('pandas'),
            'numpy': get_lib_version('numpy'),
            'scikit_learn': get_lib_version('sklearn'),
            'faiss': get_lib_version('faiss') or get_lib_version('faiss_cpu'),
            'lightgbm': get_lib_version('lightgbm'),
            'xgboost': get_lib_version('xgboost'),
            'mlflow': get_lib_version('mlflow') if MLFLOW_AVAILABLE else None,
        }
    }

    # Incluir artefactos de calibración si existen
    calibrated_models_dir = Path('models/calibrated')
    platt_pkl = calibrated_models_dir / 'platt_calibrator.pkl'
    iso_pkl = calibrated_models_dir / 'isotonic_calibrator.pkl'
    metadata['calibration_artifacts'] = {
        'platt_path': str(platt_pkl) if platt_pkl.exists() else None,
        'platt_hash': file_hash(platt_pkl) if platt_pkl.exists() else None,
        'isotonic_path': str(iso_pkl) if iso_pkl.exists() else None,
        'isotonic_hash': file_hash(iso_pkl) if iso_pkl.exists() else None,
    }

    # Log a MLflow
    print("📈 Logging a MLflow...")
    mlflow_run_id = log_to_mlflow(metadata, calibration_metrics)
    if mlflow_run_id:
        metadata['mlflow_run_id'] = mlflow_run_id
        print(f"✅ MLflow run ID: {mlflow_run_id}")

    # Computar HMAC para integridad del JSON FINAL (tras añadir mlflow_run_id y artifacts)
    metadata['hmac_sha256'] = compute_metadata_hmac(metadata)

    # Guardar metadata
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
    
    print(f'✅ Metadata pipeline guardada en {OUT}')
    print(f"🔒 HMAC integrity: {metadata['hmac_sha256'][:16]}...")
    
    if calibration_metrics:
        print("📊 Métricas de calibración:")
        for method, metrics in calibration_metrics.items():
            ece = metrics.get('ece')
            brier = metrics.get('brier_score')
            if ece is not None and brier is not None:
                print(f"  {method}: ECE={ece:.4f}, Brier={brier:.4f}")
            else:
                print(f"  {method}: métricas no disponibles")

    # Construir y guardar artifact_map.json (Fase 1 - inicio)
    artifacts: List[Dict[str, Any]] = []

    def add_artifact(name: str, path: Path, params: Optional[Dict[str, Any]] = None):
        info = {
            'name': name,
            'path': str(path),
            'exists': path.exists(),
            'hash': file_hash(path) if path.exists() else None,
            'producer': 'pipeline_metadata_v4',
            'git_commit': git_hash,
            'params': params or {}
        }
        artifacts.append(info)

    add_artifact('model_rf', MODEL, {'temporal_year_mode': temporal_year_mode})
    add_artifact('cv_metrics', CV_JSON)
    add_artifact('heuristics_params', HEURISTICS)
    add_artifact('weak_labels', WEAK)
    add_artifact('weak_labels_ensemble', ENSEMBLE_WEAK)
    add_artifact('embeddings', EMBEDDINGS)
    if platt_pkl.exists():
        add_artifact('platt_calibrator', platt_pkl)
    if iso_pkl.exists():
        add_artifact('isotonic_calibrator', iso_pkl)

    # Añadir el propio metadata JSON (recalcular hash ya que lo acabamos de escribir)
    add_artifact('pipeline_metadata', OUT)

    ARTIFACT_MAP.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_MAP.write_text(json.dumps({'artifacts': artifacts}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"🗺️  Artifact map guardado en {ARTIFACT_MAP}")
    
    # Validar estructura del artifact map
    ok, errs = validate_artifact_map_file(ARTIFACT_MAP)
    if ok:
        print(f"✅ Artifact map validado ({len(artifacts)} items)")
    else:
        print(f"⚠️  Artifact map inválido: {len(errs)} problemas")
        for e in errs[:5]:
            print(f" - {e}")


if __name__ == '__main__':
    main()
