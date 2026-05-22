# Plausibility Model Comparison (v4)

Generated: 2025-09-15T23:52:16.109492Z

## Baseline
{
  "available": true,
  "auc": 1.0,
  "f1": 1.0,
  "f1_opt": 1.0,
  "threshold_opt": 0.33000000000000007,
  "brier": 0.008262333333333335,
  "ece": 0.04883333333333338,
  "overfit_risk": true,
  "alt_models": {
    "rf_regularized": {
      "auc": 1.0,
      "f1_default": 1.0,
      "f1_opt": 1.0,
      "thr_opt": 0.45000000000000007,
      "brier": 0.049821915075513826
    },
    "lightgbm": {
      "auc": 1.0,
      "f1_default": 0.98989898989899,
      "f1_opt": 0.98989898989899,
      "thr_opt": 0.2
    },
    "xgboost": {
      "auc": 1.0,
      "f1_default": 1.0,
      "f1_opt": 1.0,
      "thr_opt": 0.2
    }
  },
  "cv": {
    "auc_mean": 0.9994397759103641,
    "auc_std": 0.0011204481792717047,
    "f1_mean": 0.9960380504069825,
    "f1_std": 0.004853962774600215
  }
}

## Other Models
- rf_regularized: AUC=0.9994879672299027 ΔAUC=-0.0005120327700972593 F1_opt=None
- no_cits_rf: AUC=1.0 ΔAUC=0.0 F1_opt=1.0
- logreg: AUC=0.8374295954941116 ΔAUC=-0.16257040450588844 F1_opt=0.875
