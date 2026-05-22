from __future__ import annotations
from pathlib import Path
import json
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.metrics import roc_auc_score, f1_score, brier_score_loss, confusion_matrix
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV

ENRICHED = Path('data/plausibility_training_v4_enriched.jsonl')
CLUSTERS = Path('data/plausibility_training_v4_clusters.parquet')
WEAK = Path('data/plausibility_training_v4_weak_labels.parquet')
MODEL_OUT = Path('models/plausibility_v4_rf.pkl')
CV_REPORT = Path('models/plausibility_v4_cv_metrics.json')

"""Entrenamiento del modelo de plausibilidad v4 con CV estratificada.

Genera:
 - models/plausibility_v4_rf.pkl (incluye métricas simple holdout y CV)
 - models/plausibility_v4_cv_metrics.json (promedios y desviaciones AUC/F1)
"""

FEATURE_COLS = [
    'title_len','abstract_len','citation_count','influential_citation_count',
    'influential_ratio','recency_years','fields_count','abstract_title_len_ratio'
]

def expected_calibration_error(y_true, proba, n_bins: int = 15):
    if len(proba) == 0:
        return float('nan')
    bins = np.linspace(0.0, 1.0, n_bins+1)
    ece = 0.0
    for i in range(n_bins):
        mask = (proba >= bins[i]) & (proba < bins[i+1]) if i < n_bins-1 else (proba >= bins[i]) & (proba <= bins[i+1])
        if not np.any(mask):
            continue
        bin_conf = proba[mask].mean()
        bin_acc = y_true[mask].mean()
        ece += (mask.sum()/len(proba)) * abs(bin_acc - bin_conf)
    return float(ece)

def best_threshold(y_true, proba, grid=None):
    if grid is None:
        grid = np.linspace(0.2, 0.8, 61)
    best_t, best_f1 = 0.5, -1
    for t in grid:
        preds = (proba >= t).astype(int)
        f1 = f1_score(y_true, preds)
        if f1 > best_f1:
            best_f1 = f1
            best_t = t
    return float(best_t), float(best_f1)

def try_lightgbm():  # pragma: no cover
    try:
        import lightgbm as lgb
        return lgb
    except Exception:
        return None

def try_xgboost():  # pragma: no cover
    try:
        import xgboost as xgb
        return xgb
    except Exception:
        return None


def load_enriched_df() -> pd.DataFrame:
    if not ENRICHED.exists():
        return pd.DataFrame([])
    rows = [json.loads(line) for line in ENRICHED.read_text(encoding='utf-8').splitlines() if line.strip()]
    return pd.DataFrame(rows)


def build_dataset():
    df_e = load_enriched_df()
    if df_e.empty:
        raise SystemExit('Enriched dataset vacío')
    if CLUSTERS.exists():
        df_c = pd.read_parquet(CLUSTERS)[['paper_id','cluster_id']]
        df_e = df_e.merge(df_c, on='paper_id', how='left')
    else:
        df_e['cluster_id'] = -1
    if WEAK.exists():
        df_w = pd.read_parquet(WEAK)
        df_e = df_e.merge(df_w, on='paper_id', how='left')
    else:
        raise SystemExit('Weak labels no encontrados')
    return df_e


def run_cv(X, y, n_splits=5, seed=42):
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    aucs, f1s = [], []
    for train_idx, test_idx in skf.split(X, y):
        X_tr, X_te = X.iloc[train_idx], X.iloc[test_idx]
        y_tr, y_te = y.iloc[train_idx], y.iloc[test_idx]
        clf = RandomForestClassifier(n_estimators=300, n_jobs=-1, random_state=seed, class_weight='balanced')
        clf.fit(X_tr, y_tr)
        proba = clf.predict_proba(X_te)[:,1]
        aucs.append(roc_auc_score(y_te, proba))
        f1s.append(f1_score(y_te, (proba>=0.5).astype(int)))
    return {'auc_mean': float(np.mean(aucs)), 'auc_std': float(np.std(aucs)), 'f1_mean': float(np.mean(f1s)), 'f1_std': float(np.std(f1s))}


def temporal_split_subset(df: pd.DataFrame):
    """If a 'year' column exists, create a pseudo temporal evaluation subset.

    Strategy:
    - Determine median year; treat records with year <= median as temporal_train, > median as temporal_test.
    - Return (temporal_train_idx, temporal_test_idx) or (None,None) if not applicable / insufficient coverage.
    """
    if 'year' not in df.columns:
        return None, None
    years = df['year'].dropna()
    if years.empty or years.nunique() < 4:
        return None, None
    median_year = np.median(years)
    temporal_train_idx = df.index[df['year'] <= median_year].tolist()
    temporal_test_idx = df.index[df['year'] > median_year].tolist()
    if len(temporal_train_idx) < 30 or len(temporal_test_idx) < 30:
        return None, None
    return temporal_train_idx, temporal_test_idx

def main():
    df = build_dataset()
    df['cluster_id'] = df['cluster_id'].fillna(-1)
    # Preparar X
    X_num = df[FEATURE_COLS].fillna(0)
    # One-hot simple para cluster (limitar número)
    if df['cluster_id'].nunique() < 200:
        X_cluster = pd.get_dummies(df['cluster_id'].astype(int), prefix='cl')
        X = pd.concat([X_num, X_cluster], axis=1)
    else:
        X = X_num
    y = df['weak_label'].fillna(0).astype(int)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    clf = RandomForestClassifier(n_estimators=300, max_depth=None, n_jobs=-1, random_state=42, class_weight='balanced')
    clf.fit(X_train, y_train)
    proba = clf.predict_proba(X_test)[:,1]
    opt_thr, f1_opt = best_threshold(y_test, proba)
    auc = roc_auc_score(y_test, proba)
    f1 = f1_score(y_test, (proba >= 0.5).astype(int))
    brier = brier_score_loss(y_test, proba)
    cm = confusion_matrix(y_test, (proba >= opt_thr).astype(int)).tolist()
    overfit_risk = bool(auc > 0.995 and f1_opt > 0.98)
    ece = expected_calibration_error(y_test.values, proba)

    # Calibración (Platt / Isotónica) usando 3-fold internamente sobre holdout base
    calibrated = {}
    try:
        sig_clf = CalibratedClassifierCV(base_estimator=clf, method='sigmoid', cv=3)
        sig_clf.fit(X_train, y_train)
        proba_sig = sig_clf.predict_proba(X_test)[:,1]
        thr_sig, f1_sig = best_threshold(y_test, proba_sig)
        calibrated['platt'] = {
            'auc': roc_auc_score(y_test, proba_sig),
            'brier': brier_score_loss(y_test, proba_sig),
            'ece': expected_calibration_error(y_test.values, proba_sig),
            'f1_opt': f1_sig,
            'thr_opt': thr_sig
        }
    except Exception:
        pass
    try:
        iso_clf = CalibratedClassifierCV(base_estimator=clf, method='isotonic', cv=3)
        iso_clf.fit(X_train, y_train)
        proba_iso = iso_clf.predict_proba(X_test)[:,1]
        thr_iso, f1_iso = best_threshold(y_test, proba_iso)
        calibrated['isotonic'] = {
            'auc': roc_auc_score(y_test, proba_iso),
            'brier': brier_score_loss(y_test, proba_iso),
            'ece': expected_calibration_error(y_test.values, proba_iso),
            'f1_opt': f1_iso,
            'thr_opt': thr_iso
        }
    except Exception:
        pass
    # LightGBM / XGBoost opcionales
    lgb_mod = try_lightgbm()
    xgb_mod = try_xgboost()
    alt_models = {}
    # RF regularizado alternativo si overfit
    if overfit_risk:
        rf_reg = RandomForestClassifier(n_estimators=200, max_depth=8, min_samples_leaf=10, n_jobs=-1, random_state=42, class_weight='balanced')
        rf_reg.fit(X_train, y_train)
        proba_reg = rf_reg.predict_proba(X_test)[:,1]
        thr_reg, f1_reg_opt = best_threshold(y_test, proba_reg)
        alt_models['rf_regularized'] = {
            'auc': roc_auc_score(y_test, proba_reg),
            'f1_default': f1_score(y_test, (proba_reg>=0.5).astype(int)),
            'f1_opt': f1_reg_opt,
            'thr_opt': thr_reg,
            'brier': brier_score_loss(y_test, proba_reg)
        }
    if lgb_mod:
        try:
            d_train = lgb_mod.Dataset(X_train, label=y_train)
            params = {'objective':'binary','learning_rate':0.05,'num_leaves':31,'verbose':-1,'feature_fraction':0.9,'bagging_fraction':0.8,'bagging_freq':1,'seed':42}
            lgbm = lgb_mod.train(params, d_train, num_boost_round=200)
            proba_lgb = np.asarray(lgbm.predict(X_test), dtype=float)
            thr_lgb, f1_lgb = best_threshold(y_test, proba_lgb)
            alt_models['lightgbm'] = {
                'auc': roc_auc_score(y_test, proba_lgb),
                'f1_default': f1_score(y_test, (proba_lgb>=0.5).astype(int)),
                'f1_opt': f1_lgb,
                'thr_opt': thr_lgb
            }
        except Exception:
            pass
    if xgb_mod:
        try:
            dtrain = xgb_mod.DMatrix(X_train, label=y_train)
            dtest = xgb_mod.DMatrix(X_test, label=y_test)
            params = {'objective':'binary:logistic','eta':0.05,'max_depth':6,'subsample':0.8,'colsample_bytree':0.8,'eval_metric':'auc','seed':42}
            xgbm = xgb_mod.train(params, dtrain, num_boost_round=400)
            proba_xgb = np.asarray(xgbm.predict(dtest), dtype=float)
            thr_xgb, f1_xgb = best_threshold(y_test, proba_xgb)
            alt_models['xgboost'] = {
                'auc': roc_auc_score(y_test, proba_xgb),
                'f1_default': f1_score(y_test, (proba_xgb>=0.5).astype(int)),
                'f1_opt': f1_xgb,
                'thr_opt': thr_xgb
            }
        except Exception:
            pass
    
    # Temporal evaluation (optional)
    temporal_metrics = None
    tr_idx, te_idx = temporal_split_subset(df)
    if tr_idx and te_idx:
        X_tem_tr, X_tem_te = X.loc[tr_idx], X.loc[te_idx]
        y_tem_tr, y_tem_te = y.loc[tr_idx], y.loc[te_idx]
        temporal_clf = RandomForestClassifier(n_estimators=300, n_jobs=-1, random_state=42, class_weight='balanced')
        temporal_clf.fit(X_tem_tr, y_tem_tr)
        proba_tem = temporal_clf.predict_proba(X_tem_te)[:,1]
        thr_tem, f1_tem_opt = best_threshold(y_tem_te, proba_tem)
        temporal_metrics = {
            'train_years_range': [int(df.loc[tr_idx, 'year'].min()), int(df.loc[tr_idx,'year'].max())],
            'test_years_range': [int(df.loc[te_idx, 'year'].min()), int(df.loc[te_idx,'year'].max())],
            'auc': roc_auc_score(y_tem_te, proba_tem),
            'f1_default': f1_score(y_tem_te, (proba_tem>=0.5).astype(int)),
            'f1_opt': f1_tem_opt,
            'thr_opt': thr_tem,
            'brier': brier_score_loss(y_tem_te, proba_tem)
        }

    MODEL_OUT.parent.mkdir(parents=True, exist_ok=True)
    cv_metrics = run_cv(X, y, n_splits=5, seed=42)
    CV_REPORT.parent.mkdir(parents=True, exist_ok=True)
    CV_REPORT.write_text(json.dumps(cv_metrics, ensure_ascii=False, indent=2), encoding='utf-8')
    joblib.dump({
        'model': clf,
        'feature_columns': list(X.columns),
        'auc': auc,
        'f1': f1,
        'threshold_opt': opt_thr,
        'f1_opt': f1_opt,
        'brier': brier,
        'ece': ece,
        'confusion_matrix_opt_thr': cm,
        'overfit_risk': overfit_risk,
        'cv': cv_metrics,
        'alt_models': alt_models,
    'temporal_metrics': temporal_metrics,
    'calibration': calibrated
    }, MODEL_OUT)
    msg = (f"Modelo guardado: {MODEL_OUT} RF AUC={auc:.4f} F1={f1:.4f} F1_opt={f1_opt:.4f}@thr={opt_thr:.2f} "
           f"Brier={brier:.4f} ECE={ece:.4f} OverfitRisk={overfit_risk} | CV AUC={cv_metrics['auc_mean']:.4f}±{cv_metrics['auc_std']:.4f}")
    if temporal_metrics:
        msg += f" | Temporal AUC={temporal_metrics['auc']:.4f} F1_opt={temporal_metrics['f1_opt']:.4f}"
    if calibrated:
        msg += " | Calibrations:" + ",".join([f"{k}:ECE={v['ece']:.4f}" for k,v in calibrated.items()])
    print(msg)


if __name__ == '__main__':
    main()
