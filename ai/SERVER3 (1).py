"""
GenoScene ML Server v3.0
========================
FastAPI server based on the new Ensemble notebook:
  Merged_LightGBM_LGBMClassifier_Ensemble_Fold.ipynb

Pipeline per trait (Eye / Hair / Skin):
  1. VarianceThreshold  → removes near-constant SNPs
  2. Gene-Group Feature Engineering (MC1R, HERC2_OCA2, SLC, TYR + interactions)
  3. RandomForest feature selection (top-N per trait)
  4. BorderlineSMOTE oversampling on train split only
  5. 8 Candidates: LogReg, LightGBM (Optuna), XGBoost (Optuna),
                   HistGB, SVC, RandomForest, TabNet, Stacking
  6. CalibratedClassifierCV on held-out calibration set (all models)
  7. Best model picked by Macro-F1 then Log-Loss

Endpoints:
  POST /analyze        → upload CSV → full predictions
  GET  /health         → server status
  GET  /model-info     → per-trait model details + metrics

Usage:
  pip install fastapi uvicorn scikit-learn xgboost lightgbm pytorch-tabnet \
              optuna imbalanced-learn pandas numpy
  python SERVER3.py
"""

# ──────────────────────────────────────────────────────────────────
# Imports
# ──────────────────────────────────────────────────────────────────
import io
import os
import time
import logging
import warnings
import numpy as np
import pandas as pd
from collections import Counter
from datetime import datetime
from typing import Any, Dict, List, Optional

warnings.filterwarnings("ignore")

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# sklearn
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import (
    HistGradientBoostingClassifier,
    RandomForestClassifier,
    StackingClassifier,
)
from sklearn.feature_selection import VarianceThreshold
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, log_loss
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.svm import SVC
from sklearn.utils.class_weight import compute_sample_weight

# Boosting
from xgboost import XGBClassifier
import lightgbm as lgb

# Optuna
import optuna
optuna.logging.set_verbosity(optuna.logging.WARNING)

# SMOTE
from imblearn.over_sampling import BorderlineSMOTE, RandomOverSampler

# TabNet
from pytorch_tabnet.tab_model import TabNetClassifier

# ──────────────────────────────────────────────────────────────────
# Logging
# ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("GenoScene-v3")

# ──────────────────────────────────────────────────────────────────
# Global state
# ──────────────────────────────────────────────────────────────────
models_store: Dict[str, Any] = {}        # trained models & metadata
training_meta: Dict[str, Any] = {}       # timing / dataset info

app = FastAPI(
    title="GenoScene ML Server",
    version="3.0.0",
    description="SNP-based phenotype prediction — Eye / Hair / Skin",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────────────────────────
# Configuration — mirrors the notebook exactly
# ──────────────────────────────────────────────────────────────────
EYE_TARGET   = "Predicted_Eye_Color"
HAIR_TARGET  = "Predicted_Hair_Color"
SKIN_TARGET  = "Predicted_Skin_Color"
SKIN_MERGED  = "Predicted_Skin_Color_merged"

VARIANCE_THRESHOLD = 0.01

# Gene groups — subset matching (rs-prefix matching against column names)
GENE_GROUPS: Dict[str, List[str]] = {
    "MC1R":       ["rs1805005", "rs1805006", "rs1805007", "rs1805008",
                   "rs1805009", "rs2228479", "rs11547464", "rs885479", "rs1110400"],
    "HERC2_OCA2": ["rs12913832", "rs1129038", "rs1470608", "rs1800407", "rs12896399"],
    "SLC":        ["rs1426654", "rs16891982", "rs28777"],
    "TYR":        ["rs1042602", "rs1393350", "rs1126809"],
}

# Number of top features to select per trait
TARGET_N_FEATURES = {"Eye Color": 15, "Hair Color": 35, "Skin Color": 30}

# Optuna trials per model (reduce for faster startup; increase for better tuning)
OPTUNA_TRIALS = 15


# ══════════════════════════════════════════════════════════════════
# Helper utilities
# ══════════════════════════════════════════════════════════════════

def _entropy(probs: np.ndarray) -> float:
    return float(-np.sum(probs * np.log(probs + 1e-9)))


def _uncertainty(ent: float) -> str:
    if ent < 0.3:
        return "Very High Confidence"
    if ent < 0.7:
        return "Moderate Confidence"
    return "Low Confidence"


def _compute_metrics(y_true, y_pred, y_proba, n_classes) -> Dict[str, float]:
    return {
        "Accuracy": round(accuracy_score(y_true, y_pred), 4),
        "Macro_F1": round(f1_score(y_true, y_pred, average="macro", zero_division=0), 4),
        "Log_Loss": round(log_loss(y_true, y_proba, labels=list(range(n_classes))), 4),
    }


def _find_dataset() -> Optional[str]:
    candidates = [
        os.path.join(os.path.dirname(__file__), "final_merged_3.csv"),
        os.path.join(os.path.dirname(__file__), "..", "final_merged_3.csv"),
        "final_merged_3.csv",
    ]
    for p in candidates:
        if os.path.isfile(p):
            return p
    return None


# ══════════════════════════════════════════════════════════════════
# TabNet sklearn-compatible wrapper  (same as notebook)
# ══════════════════════════════════════════════════════════════════

class TabNetWrapper(ClassifierMixin, BaseEstimator):
    """Thin sklearn-API wrapper around TabNetClassifier — compatible with sklearn >= 1.4."""

    # Explicitly mark as classifier for newer sklearn versions
    _estimator_type = "classifier"

    def __init__(self, n_d=32, n_a=32, n_steps=5, gamma=1.5,
                 optimizer_params=None, scheduler_params=None, verbose=0):
        self.n_d = n_d
        self.n_a = n_a
        self.n_steps = n_steps
        self.gamma = gamma
        self.optimizer_params = optimizer_params
        self.scheduler_params = scheduler_params
        self.verbose = verbose

    def fit(self, X, y, **fit_params):
        self.classes_ = np.unique(y)
        self.n_classes_ = len(self.classes_)
        opt_params = self.optimizer_params if self.optimizer_params is not None else dict(lr=2e-2)
        sch_params = self.scheduler_params if self.scheduler_params is not None else {"step_size": 10, "gamma": 0.9}
        self.model_ = TabNetClassifier(
            n_d=self.n_d, n_a=self.n_a, n_steps=self.n_steps, gamma=self.gamma,
            optimizer_params=opt_params,
            scheduler_params=sch_params,
            verbose=self.verbose,
        )
        self.model_.fit(X.astype(np.float32), y, **fit_params)
        return self

    def predict(self, X) -> np.ndarray:
        return self.model_.predict(X.astype(np.float32))

    def predict_proba(self, X) -> np.ndarray:
        return self.model_.predict_proba(X.astype(np.float32))

    def __sklearn_tags__(self):
        tags = super().__sklearn_tags__()
        tags.estimator_type = "classifier"
        return tags


# ══════════════════════════════════════════════════════════════════
# Feature Engineering
# ══════════════════════════════════════════════════════════════════

def _build_gene_features(df: pd.DataFrame,
                         selected_snps: List[str]) -> tuple:
    """
    Add gene-group sum/mean columns and interaction features.
    Returns (df_augmented, gene_group_cols, gene_group_recipe).
    Recipe is needed to reproduce the same features at inference time.
    """
    gene_group_cols: List[str] = []
    # recipe: { col_name -> {"type": "sum"|"mean"|"interaction", "sources": [...]} }
    recipe: Dict[str, Any] = {}

    for group_name, rs_ids in GENE_GROUPS.items():
        # Match by substring — handles allele suffix (e.g., "rs1805005" matches "rs1805005_T")
        cols = [s for s in selected_snps if any(rs in s for rs in rs_ids)]
        if len(cols) >= 2:
            sum_col  = f"{group_name}_sum"
            mean_col = f"{group_name}_mean"
            df[sum_col]  = df[cols].sum(axis=1)
            df[mean_col] = df[cols].mean(axis=1)
            gene_group_cols += [sum_col, mean_col]
            recipe[sum_col]  = {"type": "sum",  "sources": cols}
            recipe[mean_col] = {"type": "mean", "sources": cols}
            log.info(f"  Gene feature: {group_name} ({len(cols)} SNPs) → {sum_col}, {mean_col}")

    # Interaction features
    for (a, b, name) in [
        ("MC1R_sum", "HERC2_OCA2_sum", "MC1R_x_HERC2"),
        ("MC1R_sum", "SLC_sum",        "MC1R_x_SLC"),
    ]:
        if a in df.columns and b in df.columns:
            df[name] = df[a] * df[b]
            gene_group_cols.append(name)
            recipe[name] = {"type": "interaction", "sources": [a, b]}
            log.info(f"  Interaction feature: {name}")

    return df, gene_group_cols, recipe


def _apply_gene_recipe(df_in: pd.DataFrame,
                       recipe: Dict[str, Any]) -> pd.DataFrame:
    """Reproduce gene-group features on inference data using the stored recipe."""
    df_in = df_in.copy()
    for col, info in recipe.items():
        t = info["type"]
        srcs = info["sources"]
        if t == "sum":
            df_in[col] = df_in[[s for s in srcs if s in df_in.columns]].sum(axis=1)
        elif t == "mean":
            present = [s for s in srcs if s in df_in.columns]
            df_in[col] = df_in[present].mean(axis=1) if present else 0.0
        elif t == "interaction":
            a, b = srcs
            df_in[col] = df_in.get(a, pd.Series(0.0, index=df_in.index)) * \
                         df_in.get(b, pd.Series(0.0, index=df_in.index))
    return df_in


# ══════════════════════════════════════════════════════════════════
# SMOTE helper  (same logic as notebook)
# ══════════════════════════════════════════════════════════════════

def _apply_smote(X: np.ndarray, y: np.ndarray):
    min_count = min(Counter(y).values())
    if min_count < 2:
        log.info("    SMOTE skipped (class with <2 samples)")
        return X, y
    if min_count <= 5:
        ros = RandomOverSampler(random_state=42)
        Xr, yr = ros.fit_resample(X, y)
        log.info(f"    RandomOverSampler: {len(y)} → {len(yr)}")
        return Xr, yr
    try:
        k = min(5, min_count - 1)
        sm = BorderlineSMOTE(random_state=42, k_neighbors=k)
        Xr, yr = sm.fit_resample(X, y)
        log.info(f"    BorderlineSMOTE: {len(y)} → {len(yr)}")
        return Xr, yr
    except Exception:
        ros = RandomOverSampler(random_state=42)
        Xr, yr = ros.fit_resample(X, y)
        log.info(f"    Fallback RandomOverSampler: {len(y)} → {len(yr)}")
        return Xr, yr


# ══════════════════════════════════════════════════════════════════
# Optuna tuning helpers
# ══════════════════════════════════════════════════════════════════

def _optuna_xgb(X_train: np.ndarray, y_train: np.ndarray,
                n_classes: int, n_trials: int = OPTUNA_TRIALS) -> Dict:
    def objective(trial):
        params = {
            "n_estimators":    trial.suggest_int("n_estimators", 200, 600),
            "max_depth":       trial.suggest_int("max_depth", 3, 8),
            "learning_rate":   trial.suggest_float("learning_rate", 0.01, 0.15),
            "subsample":       trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree":trial.suggest_float("colsample_bytree", 0.6, 1.0),
            "min_child_weight":trial.suggest_int("min_child_weight", 1, 10),
            "reg_alpha":       trial.suggest_float("reg_alpha", 1e-8, 10.0, log=True),
            "reg_lambda":      trial.suggest_float("reg_lambda", 1e-8, 10.0, log=True),
        }
        mdl = XGBClassifier(
            **params, objective="multi:softprob", num_class=n_classes,
            random_state=42, verbosity=0, n_jobs=-1)
        skf = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
        scores = []
        for tr, va in skf.split(X_train, y_train):
            mdl.fit(X_train[tr], y_train[tr])
            scores.append(f1_score(y_train[va], mdl.predict(X_train[va]), average="macro"))
        return np.mean(scores)

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=n_trials, show_progress_bar=False)
    log.info(f"    XGB Optuna best CV-F1={study.best_value:.4f}")
    return study.best_params


def _optuna_lgbm(X_train: np.ndarray, y_train: np.ndarray,
                 n_classes: int, n_trials: int = OPTUNA_TRIALS) -> Dict:
    obj = "multiclass" if n_classes > 2 else "binary"

    def objective(trial):
        params = {
            "n_estimators":      trial.suggest_int("n_estimators", 200, 600),
            "num_leaves":        trial.suggest_int("num_leaves", 15, 63),
            "learning_rate":     trial.suggest_float("learning_rate", 0.01, 0.15),
            "subsample":         trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree":  trial.suggest_float("colsample_bytree", 0.6, 1.0),
            "min_child_samples": trial.suggest_int("min_child_samples", 5, 50),
            "reg_alpha":         trial.suggest_float("reg_alpha", 1e-8, 10.0, log=True),
            "reg_lambda":        trial.suggest_float("reg_lambda", 1e-8, 10.0, log=True),
        }
        mdl = lgb.LGBMClassifier(
            **params, objective=obj,
            num_class=n_classes if obj == "multiclass" else None,
            class_weight="balanced" if obj == "multiclass" else None,
            random_state=42, n_jobs=-1, verbose=-1)
        skf = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
        scores = []
        for tr, va in skf.split(X_train, y_train):
            mdl.fit(X_train[tr], y_train[tr])
            scores.append(f1_score(y_train[va], mdl.predict(X_train[va]), average="macro"))
        return np.mean(scores)

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=n_trials, show_progress_bar=False)
    log.info(f"    LGBM Optuna best CV-F1={study.best_value:.4f}")
    return study.best_params


# ══════════════════════════════════════════════════════════════════
# Core training function  (one trait at a time)
# ══════════════════════════════════════════════════════════════════

def _train_trait(trait_name: str,
                 target_col: str,
                 feature_cols: List[str],
                 df_data: pd.DataFrame) -> Dict[str, Any]:
    """
    Train all 8 candidates for one trait.
    Returns structured dict with models, metrics, feature_cols.
    """
    le = LabelEncoder()
    y_all = le.fit_transform(df_data[target_col].astype(str))
    classes = le.classes_
    n_classes = len(classes)
    X_all = df_data[feature_cols].values

    log.info(f"\n{'='*60}")
    log.info(f"  {trait_name}  |  {n_classes} classes: {list(classes)}  |  {len(feature_cols)} features")
    log.info(f"{'='*60}")

    # ── 3-way split: 70% train / 10% calibration / 20% test ──────
    X_tv, X_test, y_tv, y_test = train_test_split(
        X_all, y_all, test_size=0.2, random_state=42, stratify=y_all)
    X_train, X_calib, y_train, y_calib = train_test_split(
        X_tv, y_tv, test_size=0.125, random_state=42, stratify=y_tv)
    log.info(f"  Split: train={len(y_train)}, calib={len(y_calib)}, test={len(y_test)}")

    # ── SMOTE on train only ───────────────────────────────────────
    X_sm, y_sm = _apply_smote(X_train, y_train)

    # Early-stopping val split (for LGBM + TabNet)
    X_tr, X_es, y_tr, y_es = train_test_split(
        X_sm, y_sm, test_size=0.15, random_state=42, stratify=y_sm)

    # ── Calibration method & cv_folds — dynamic based on calib size ──
    min_cal = min(Counter(y_calib).values())
    cal_method = "sigmoid" if min_cal < 10 else "isotonic"
    # FIX: CalibratedClassifierCV requires cv >= 2 (integer only, no "prefit" string)
    # When a class has very few calib samples, duplicate them so cv=2 works safely
    if min_cal < 2:
        log.info(f"  WARNING: min calib class has {min_cal} sample(s) — duplicating calib set to allow cv=2")
        X_calib = np.vstack([X_calib, X_calib])
        y_calib = np.concatenate([y_calib, y_calib])
    cv_folds = min(3, min(Counter(y_calib).values()))
    cv_folds = max(cv_folds, 2)  # ensure at least 2
    log.info(f"  Calibration method: {cal_method} (min calib class={min_cal}, cv={cv_folds})")

    obj_type = "multiclass" if n_classes > 2 else "binary"

    # Storage
    trained_models: Dict[str, Any] = {}
    metrics_dict:   Dict[str, Any] = {}
    preds_dict:     Dict[str, Any] = {}

    def _register(name: str, model):
        pred  = model.predict(X_test)
        proba = model.predict_proba(X_test)
        trained_models[name] = model
        metrics_dict[name]   = _compute_metrics(y_test, pred, proba, n_classes)
        preds_dict[name]     = pred
        m = metrics_dict[name]
        log.info(f"    {name:<12s}  Acc={m['Accuracy']:.4f}  "
                 f"F1={m['Macro_F1']:.4f}  Loss={m['Log_Loss']:.4f}")

    # ── 1. Logistic Regression ────────────────────────────────────
    log.info("  [1/8] LogisticRegression")
    lr = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(solver="lbfgs", max_iter=2000,
                                   class_weight="balanced")),
    ])
    lr.fit(X_sm, y_sm)
    lr_cal = CalibratedClassifierCV(lr, method=cal_method, cv=cv_folds)
    lr_cal.fit(X_calib, y_calib)
    _register("LogReg", lr_cal)

    # ── 2. LightGBM (Optuna-tuned) ────────────────────────────────
    log.info("  [2/8] LightGBM (Optuna)")
    lgbm_params = _optuna_lgbm(X_sm, y_sm, n_classes)
    lgbm_m = lgb.LGBMClassifier(
        **lgbm_params, objective=obj_type,
        num_class=n_classes if obj_type == "multiclass" else None,
        class_weight="balanced" if obj_type == "multiclass" else None,
        random_state=42, n_jobs=-1, verbose=-1)
    lgbm_m.fit(X_tr, y_tr,
               eval_set=[(X_es, y_es)],
               callbacks=[lgb.early_stopping(stopping_rounds=25, verbose=False)])
    lgbm_cal = CalibratedClassifierCV(lgbm_m, method=cal_method, cv=cv_folds)
    lgbm_cal.fit(X_calib, y_calib)
    _register("LGBM", lgbm_cal)

    # ── 3. XGBoost (Optuna-tuned) ─────────────────────────────────
    log.info("  [3/8] XGBoost (Optuna)")
    xgb_params = _optuna_xgb(X_sm, y_sm, n_classes)
    xgb_m = XGBClassifier(
        **xgb_params, objective="multi:softprob", num_class=n_classes,
        random_state=42, verbosity=0, n_jobs=-1)
    xgb_m.fit(X_sm, y_sm)
    xgb_cal = CalibratedClassifierCV(xgb_m, method=cal_method, cv=cv_folds)
    xgb_cal.fit(X_calib, y_calib)
    _register("XGB", xgb_cal)

    # ── 4. HistGradientBoosting ───────────────────────────────────
    log.info("  [4/8] HistGradientBoosting")
    hist_m = HistGradientBoostingClassifier(
        max_iter=300, max_depth=5, learning_rate=0.05,
        random_state=42, class_weight="balanced")
    hist_m.fit(X_sm, y_sm)
    hist_cal = CalibratedClassifierCV(hist_m, method=cal_method, cv=cv_folds)
    hist_cal.fit(X_calib, y_calib)
    _register("HistGB", hist_cal)

    # ── 5. SVC (properly calibrated) ─────────────────────────────
    log.info("  [5/8] SVC")
    svc_pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", SVC(kernel="rbf", C=1.0, gamma="scale",
                    random_state=42, class_weight="balanced")),
    ])
    svc_pipe.fit(X_sm, y_sm)
    svc_cal = CalibratedClassifierCV(svc_pipe, method=cal_method, cv=cv_folds)
    svc_cal.fit(X_calib, y_calib)
    _register("SVC", svc_cal)

    # ── 6. RandomForest ───────────────────────────────────────────
    log.info("  [6/8] RandomForest")
    rf_m = RandomForestClassifier(
        n_estimators=300, random_state=42,
        class_weight="balanced", n_jobs=-1)
    rf_m.fit(X_sm, y_sm)
    rf_cal = CalibratedClassifierCV(rf_m, method=cal_method, cv=cv_folds)
    rf_cal.fit(X_calib, y_calib)
    _register("RF", rf_cal)

    # ── 7. TabNet ─────────────────────────────────────────────────
    log.info("  [7/8] TabNet")
    tab_m = TabNetWrapper(
        n_d=32, n_a=32, n_steps=5, gamma=1.5,
        optimizer_params=dict(lr=2e-2),
        scheduler_params={"step_size": 10, "gamma": 0.9},
        verbose=0,
    )
    tab_m.fit(
        X_sm, y_sm,
        weights=0,                                 # balanced mode (NOT per-sample)
        max_epochs=60, patience=10,
        eval_set=[(X_es.astype(np.float32), y_es)],
    )
    tab_cal = CalibratedClassifierCV(tab_m, method=cal_method, cv=cv_folds)
    tab_cal.fit(X_calib, y_calib)
    _register("TabNet", tab_cal)

    # ── 8. Stacking Ensemble ──────────────────────────────────────
    log.info("  [8/8] Stacking Ensemble")
    stack_est = [
        ("lgbm", lgb.LGBMClassifier(
            **lgbm_params, objective=obj_type,
            num_class=n_classes if obj_type == "multiclass" else None,
            class_weight="balanced" if obj_type == "multiclass" else None,
            random_state=42, n_jobs=-1, verbose=-1)),
        ("xgb", XGBClassifier(
            **xgb_params, objective="multi:softprob", num_class=n_classes,
            random_state=42, verbosity=0, n_jobs=-1)),
        ("hist", HistGradientBoostingClassifier(
            max_iter=300, max_depth=5, learning_rate=0.05,
            random_state=42, class_weight="balanced")),
        ("rf", RandomForestClassifier(
            n_estimators=300, random_state=42,
            class_weight="balanced", n_jobs=-1)),
    ]
    stacker = StackingClassifier(
        estimators=stack_est,
        final_estimator=LogisticRegression(max_iter=1000, class_weight="balanced"),
        cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
        stack_method="predict_proba",
        n_jobs=-1,
    )
    stacker.fit(X_sm, y_sm)
    # NOTE: StackingClassifier already produces calibrated probabilities via its
    # meta-estimator (LogisticRegression). Wrapping it again in CalibratedClassifierCV
    # causes shape-mismatch errors when calib folds see different class subsets.
    # So we register it directly without an extra calibration layer.
    _register("Stacking", stacker)

    # ── Print summary table ───────────────────────────────────────
    log.info(f"\n  {'Model':<12s} {'Accuracy':>10s} {'Macro_F1':>10s} {'Log_Loss':>10s}")
    log.info(f"  {'-'*44}")
    for name, m in metrics_dict.items():
        log.info(f"  {name:<12s} {m['Accuracy']:>10.4f} {m['Macro_F1']:>10.4f} {m['Log_Loss']:>10.4f}")

    return {
        "label_encoder":  le,
        "classes":        classes,
        "n_classes":      n_classes,
        "models":         trained_models,
        "metrics":        metrics_dict,
        "y_test":         y_test,
        "predictions":    preds_dict,
        "feature_cols":   feature_cols,          # needed at inference
        "optuna_params":  {"xgb": xgb_params, "lgbm": lgbm_params},
    }


# ══════════════════════════════════════════════════════════════════
# Best-model selection  (same logic as notebook)
# ══════════════════════════════════════════════════════════════════

def _choose_best(res_dict: Dict) -> tuple:
    best_name, best_m = None, None
    for name, m in res_dict["metrics"].items():
        if (best_m is None
                or m["Macro_F1"] > best_m["Macro_F1"]
                or (m["Macro_F1"] == best_m["Macro_F1"]
                    and m["Log_Loss"] < best_m["Log_Loss"])):
            best_name, best_m = name, m
    return best_name, res_dict["models"][best_name], best_m


# ══════════════════════════════════════════════════════════════════
# Full training pipeline  (runs once at startup)
# ══════════════════════════════════════════════════════════════════

def train_models():
    t0 = time.time()

    dataset_path = _find_dataset()
    if not dataset_path:
        raise FileNotFoundError(
            "Cannot find 'final_merged_3.csv'. "
            "Place it next to SERVER3.py or in the project root."
        )

    log.info(f"Loading dataset: {dataset_path}")
    df = pd.read_csv(dataset_path)
    log.info(f"Dataset shape: {df.shape}")

    # ── Raw SNP columns ───────────────────────────────────────────
    snp_cols = [c for c in df.columns if c.startswith("rs")]

    # ── NaN imputation ────────────────────────────────────────────
    nan_total = int(df[snp_cols].isna().sum().sum())
    if nan_total:
        log.info(f"Imputing {nan_total} NaN values with column mode...")
        for c in snp_cols:
            if df[c].isna().any():
                df[c] = df[c].fillna(df[c].mode().iloc[0])

    # ── VarianceThreshold ─────────────────────────────────────────
    vt = VarianceThreshold(threshold=VARIANCE_THRESHOLD)
    vt.fit(df[snp_cols].values)
    selected_snps = [snp_cols[i] for i, keep in enumerate(vt.get_support()) if keep]
    removed_snps  = [c for c in snp_cols if c not in selected_snps]
    log.info(f"VarianceThreshold: {len(selected_snps)} kept, {len(removed_snps)} removed: {removed_snps}")

    # ── Skin class merge: VeryPale → Pale ─────────────────────────
    def _clean_skin(v):
        s = str(v).strip().replace(" ", "").lower()
        mapping = {"darktoblack": "DarkToBlack", "dark": "Dark",
                   "intermediate": "Intermediate", "pale": "Pale", "verypale": "VeryPale"}
        return mapping.get(s, s)

    df[SKIN_MERGED] = df[SKIN_TARGET].map(_clean_skin).replace("VeryPale", "Pale")
    log.info(f"Skin classes after merge: {df[SKIN_MERGED].value_counts().to_dict()}")

    # ── Gene-group feature engineering ───────────────────────────
    log.info("Building gene-group features...")
    df, gene_group_cols, gene_recipe = _build_gene_features(df, selected_snps)
    all_feature_cols = selected_snps + gene_group_cols
    log.info(f"Total feature pool: {len(all_feature_cols)} "
             f"({len(selected_snps)} SNPs + {len(gene_group_cols)} gene-group)")

    # ── Per-trait feature selection via RandomForest importance ───
    targets_fs = {
        "Eye Color":  EYE_TARGET,
        "Hair Color": HAIR_TARGET,
        "Skin Color": SKIN_MERGED,
    }
    trait_feature_cols: Dict[str, List[str]] = {}

    log.info("Running per-trait RandomForest feature selection...")
    for label, target_col in targets_fs.items():
        n = TARGET_N_FEATURES[label]
        X_fs = df[all_feature_cols]
        y_fs = df[target_col].astype(str)
        rf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
        rf.fit(X_fs, y_fs)
        importances = pd.Series(rf.feature_importances_, index=all_feature_cols)
        top_n = importances.nlargest(n).index.tolist()
        trait_feature_cols[label] = top_n
        log.info(f"  {label}: Top {n} → {top_n}")

    # ── Train all 8 models per trait ──────────────────────────────
    log.info("\n" + "="*60)
    log.info("Training Eye Color models...")
    eye_res  = _train_trait("Eye Color",  EYE_TARGET,  trait_feature_cols["Eye Color"],  df)

    log.info("\n" + "="*60)
    log.info("Training Hair Color models...")
    hair_res = _train_trait("Hair Color", HAIR_TARGET, trait_feature_cols["Hair Color"], df)

    log.info("\n" + "="*60)
    log.info("Training Skin Color models...")
    skin_res = _train_trait("Skin Color", SKIN_MERGED, trait_feature_cols["Skin Color"], df)

    # ── Choose best per trait ─────────────────────────────────────
    eye_choice,  eye_model,  eye_m  = _choose_best(eye_res)
    hair_choice, hair_model, hair_m = _choose_best(hair_res)
    skin_choice, skin_model, skin_m = _choose_best(skin_res)

    log.info("\n" + "="*60)
    log.info("FINAL MODEL CHOICES")
    log.info("="*60)
    log.info(f"  Eye  → {eye_choice:<12s}  F1={eye_m['Macro_F1']:.4f}  Loss={eye_m['Log_Loss']:.4f}")
    log.info(f"  Hair → {hair_choice:<12s}  F1={hair_m['Macro_F1']:.4f}  Loss={hair_m['Log_Loss']:.4f}")
    log.info(f"  Skin → {skin_choice:<12s}  F1={skin_m['Macro_F1']:.4f}  Loss={skin_m['Log_Loss']:.4f}")

    # ── Store everything globally ─────────────────────────────────
    models_store.update({
        "eye": {
            "model":          eye_model,
            "label_encoder":  eye_res["label_encoder"],
            "classes":        eye_res["classes"],
            "feature_cols":   eye_res["feature_cols"],
            "algorithm":      eye_choice,
            "metrics":        eye_m,
            "all_metrics":    eye_res["metrics"],
        },
        "hair": {
            "model":          hair_model,
            "label_encoder":  hair_res["label_encoder"],
            "classes":        hair_res["classes"],
            "feature_cols":   hair_res["feature_cols"],
            "algorithm":      hair_choice,
            "metrics":        hair_m,
            "all_metrics":    hair_res["metrics"],
        },
        "skin": {
            "model":          skin_model,
            "label_encoder":  skin_res["label_encoder"],
            "classes":        skin_res["classes"],
            "feature_cols":   skin_res["feature_cols"],
            "algorithm":      skin_choice,
            "metrics":        skin_m,
            "all_metrics":    skin_res["metrics"],
        },
        "_gene_recipe":    gene_recipe,          # for inference reconstruction
        "_selected_snps":  selected_snps,        # raw SNPs after VT
        "_gene_group_cols": gene_group_cols,     # engineered column names
    })

    # Minimum raw SNPs needed from user CSV
    # Only collect actual SNP columns (rs-prefix), NOT gene-group features.
    # Gene-group features (e.g. HERC2_OCA2_sum) are computed server-side.
    raw_needed: set = set()
    for trait_key in ["eye", "hair", "skin"]:
        for feat in models_store[trait_key]["feature_cols"]:
            if feat in selected_snps:
                # Direct SNP column
                raw_needed.add(feat)
            elif feat in gene_recipe:
                # Gene-group / interaction feature — collect its raw SNP sources
                for src in gene_recipe[feat].get("sources", []):
                    if src in selected_snps:
                        raw_needed.add(src)
                    elif src in gene_recipe:
                        # Interaction source is itself a gene-group (e.g. MC1R_sum)
                        raw_needed.update(
                            s for s in gene_recipe[src].get("sources", [])
                            if s in selected_snps
                        )
    models_store["_raw_snps_needed"] = sorted(raw_needed)

    elapsed = round(time.time() - t0, 1)
    training_meta.update({
        "trained_at":        datetime.utcnow().isoformat() + "Z",
        "training_seconds":  elapsed,
        "dataset_rows":      len(df),
        "dataset_cols":      df.shape[1],
        "selected_snps":     len(selected_snps),
        "removed_snps":      removed_snps,
        "gene_group_cols":   gene_group_cols,
        "trait_features":    {k: len(v) for k, v in trait_feature_cols.items()},
    })
    log.info(f"\nAll models trained in {elapsed}s ✓")


# ══════════════════════════════════════════════════════════════════
# Inference helpers
# ══════════════════════════════════════════════════════════════════

def _prepare_inference_row(df_in: pd.DataFrame) -> pd.DataFrame:
    """
    Given a raw user CSV (with SNP columns), reproduce the full
    feature matrix (SNPs + gene-group + interactions) exactly as training.
    """
    df_in = df_in.copy()

    # Impute missing raw SNPs with 0
    needed_raw = models_store["_raw_snps_needed"]
    for c in needed_raw:
        if c not in df_in.columns:
            df_in[c] = 0

    # Reconstruct gene-group features using the stored recipe
    df_in = _apply_gene_recipe(df_in, models_store["_gene_recipe"])
    return df_in


def _predict_row(row: pd.Series) -> Dict[str, Any]:
    """Run inference for a single sample. Returns rich output dict."""
    result: Dict[str, Any] = {}

    for trait_key in ["eye", "hair", "skin"]:
        m     = models_store[trait_key]
        feats = m["feature_cols"]
        cls   = m["classes"]

        # Build feature vector — fill missing with 0
        x_vals = []
        for f in feats:
            x_vals.append(float(row[f]) if f in row.index else 0.0)
        X_i = np.array(x_vals).reshape(1, -1)

        proba   = m["model"].predict_proba(X_i)[0]
        top_idx = int(np.argmax(proba))
        ent     = _entropy(proba)

        result[trait_key] = {
            "top":             str(cls[top_idx]),
            "confidence_pct":  round(float(np.max(proba)) * 100, 2),
            "entropy":         round(ent, 4),
            "uncertainty":     _uncertainty(ent),
            "probabilities":   {str(c): round(float(v), 4)       for c, v in zip(cls, proba)},
            "probabilities_pct": {str(c): round(float(v)*100, 2) for c, v in zip(cls, proba)},
        }

    # Overall confidence
    result["overall_confidence"] = round(
        np.mean([result[t]["confidence_pct"] for t in ["eye", "hair", "skin"]]), 2)

    # Quick summary for mobile home screen
    result["summary"] = {
        "eye":  result["eye"]["top"],
        "hair": result["hair"]["top"],
        "skin": result["skin"]["top"],
    }
    return result


# ══════════════════════════════════════════════════════════════════
# API Endpoints
# ══════════════════════════════════════════════════════════════════

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    """
    Upload a CSV with SNP columns → get Eye / Hair / Skin predictions.

    Response per sample:
    {
      "success": true,
      "count": 1,
      "results": [
        {
          "eye":  { "top": "Blue", "confidence_pct": 98.5, "entropy": 0.05, ... },
          "hair": { "top": "Brown", ... },
          "skin": { "top": "Pale",  ... },
          "summary": { "eye": "Blue", "hair": "Brown", "skin": "Pale" },
          "overall_confidence": 97.2
        }
      ]
    }
    """
    if not models_store:
        raise HTTPException(503, detail="Models not loaded yet. Please wait.")

    content = await file.read()
    try:
        df_in = pd.read_csv(io.BytesIO(content))
    except Exception as exc:
        raise HTTPException(400, detail=f"Invalid CSV: {exc}")

    # Validate that at least the minimum raw SNPs are present
    needed = models_store["_raw_snps_needed"]
    missing = [c for c in needed if c not in df_in.columns]
    if missing:
        detail = (
            f"Missing {len(missing)} SNP columns: {missing[:10]}..."
            if len(missing) > 10
            else f"Missing SNP columns: {missing}"
        )
        raise HTTPException(400, detail=detail)

    # Reconstruct gene-group features
    df_prepared = _prepare_inference_row(df_in)

    # Predict row by row
    results = [_predict_row(df_prepared.iloc[i]) for i in range(len(df_prepared))]

    return {"success": True, "count": len(results), "results": results}


@app.get("/health")
async def health():
    """Health check — returns server status and model info."""
    loaded = bool(models_store)
    info: Dict[str, Any] = {
        "status":        "ok" if loaded else "loading",
        "version":       "3.0.0",
        "models_loaded": loaded,
    }
    if loaded:
        info["traits"] = {
            t: {
                "algorithm":    models_store[t]["algorithm"],
                "n_features":   len(models_store[t]["feature_cols"]),
                "classes":      list(models_store[t]["classes"]),
                "macro_f1":     models_store[t]["metrics"]["Macro_F1"],
            }
            for t in ["eye", "hair", "skin"]
        }
        info["training_seconds"]   = training_meta.get("training_seconds")
        info["trained_at"]         = training_meta.get("trained_at")
        info["raw_snps_required"]  = len(models_store.get("_raw_snps_needed", []))
    return info


@app.get("/model-info")
async def model_info():
    """
    Detailed per-trait model information.
    Useful for debugging and app UI (e.g., showing confidence bars).
    """
    if not models_store:
        raise HTTPException(503, detail="Models not loaded yet.")

    info: Dict[str, Any] = {}
    for trait in ["eye", "hair", "skin"]:
        m = models_store[trait]
        info[trait] = {
            "best_algorithm":  m["algorithm"],
            "best_metrics":    m["metrics"],
            "all_metrics":     m["all_metrics"],
            "n_features":      len(m["feature_cols"]),
            "feature_cols":    m["feature_cols"],
            "classes":         list(m["classes"]),
        }

    info["training_metadata"]   = training_meta
    info["gene_recipe"]         = models_store.get("_gene_recipe", {})
    info["raw_snps_required"]   = models_store.get("_raw_snps_needed", [])
    return info


@app.get("/sample-format")
async def sample_format():
    """
    Returns the list of raw SNP columns the uploaded CSV must contain.
    Useful for Flutter app to validate input before uploading.
    """
    if not models_store:
        raise HTTPException(503, detail="Models not loaded yet.")
    return {
        "required_snp_columns": models_store.get("_raw_snps_needed", []),
        "note": (
            "Upload a CSV where each row is one sample. "
            "Only raw SNP columns are required — gene-group features "
            "are computed automatically by the server."
        ),
    }


# ══════════════════════════════════════════════════════════════════
# Startup
# ══════════════════════════════════════════════════════════════════

@app.on_event("startup")
async def startup():
    log.info("GenoScene v3.0 starting — training models...")
    train_models()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=False)