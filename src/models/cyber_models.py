"""
Machine Learning Cybersecurity Analytics Suite.
Implements supervised intrusion detection (Logistic Regression, Random Forest, XGBoost, LightGBM)
and unsupervised anomaly detection (Isolation Forest) on ToN_IoT and CICIoT2023 benchmarks.
Evaluates binary and multi-class classification, per-class metrics, false-positive rate, and latency.
"""

import time
import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score,
    average_precision_score, confusion_matrix, classification_report
)
import xgboost as xgb
import lightgbm as lgb

class CyberModelSuite:
    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.trained_models: Dict[str, Any] = {}
        self.metrics_history: Dict[str, Any] = {}

    def train_evaluate_binary(self, X_train: np.ndarray, y_train: np.ndarray,
                              X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, Dict[str, Any]]:
        """
        Train and evaluate binary intrusion detection models:
        Logistic Regression, Random Forest, XGBoost, and Isolation Forest.
        """
        results = {}
        
        # 1. Logistic Regression Baseline
        print("Training Logistic Regression (Binary)...")
        lr = LogisticRegression(max_iter=1000, random_state=self.random_state, class_weight='balanced')
        t0 = time.time()
        lr.fit(X_train, y_train)
        lr_train_time = time.time() - t0
        
        t0 = time.time()
        lr_preds = lr.predict(X_test)
        lr_latency_us = ((time.time() - t0) / len(X_test)) * 1e6
        lr_probs = lr.predict_proba(X_test)[:, 1] if hasattr(lr, "predict_proba") else lr_preds
        
        results["Logistic_Regression"] = self._compute_binary_metrics(
            y_test, lr_preds, lr_probs, lr_train_time, lr_latency_us, "Logistic Regression"
        )
        self.trained_models["LR_binary"] = lr

        # 2. Random Forest Baseline
        print("Training Random Forest (Binary)...")
        rf = RandomForestClassifier(n_estimators=100, max_depth=15, n_jobs=-1,
                                    random_state=self.random_state, class_weight='balanced')
        t0 = time.time()
        rf.fit(X_train, y_train)
        rf_train_time = time.time() - t0
        
        t0 = time.time()
        rf_preds = rf.predict(X_test)
        rf_latency_us = ((time.time() - t0) / len(X_test)) * 1e6
        rf_probs = rf.predict_proba(X_test)[:, 1]
        
        results["Random_Forest"] = self._compute_binary_metrics(
            y_test, rf_preds, rf_probs, rf_train_time, rf_latency_us, "Random Forest"
        )
        self.trained_models["RF_binary"] = rf

        # 3. XGBoost
        print("Training XGBoost (Binary)...")
        scale_pos = (len(y_train) - np.sum(y_train)) / max(np.sum(y_train), 1)
        model_xgb = xgb.XGBClassifier(
            n_estimators=100, max_depth=6, learning_rate=0.1,
            scale_pos_weight=scale_pos, random_state=self.random_state,
            eval_metric="logloss", n_jobs=-1
        )
        t0 = time.time()
        model_xgb.fit(X_train, y_train)
        xgb_train_time = time.time() - t0
        
        t0 = time.time()
        xgb_preds = model_xgb.predict(X_test)
        xgb_latency_us = ((time.time() - t0) / len(X_test)) * 1e6
        xgb_probs = model_xgb.predict_proba(X_test)[:, 1]
        
        results["XGBoost"] = self._compute_binary_metrics(
            y_test, xgb_preds, xgb_probs, xgb_train_time, xgb_latency_us, "XGBoost"
        )
        self.trained_models["XGB_binary"] = model_xgb

        # 4. Isolation Forest (Unsupervised Anomaly Detection Baseline)
        print("Evaluating Isolation Forest (Anomaly Baseline)...")
        # Train strictly on benign flows (y_train == 0)
        X_train_benign = X_train[y_train == 0]
        iso = IsolationForest(n_estimators=100, contamination=0.1, random_state=self.random_state, n_jobs=-1)
        t0 = time.time()
        iso.fit(X_train_benign)
        iso_train_time = time.time() - t0
        
        t0 = time.time()
        raw_iso = iso.predict(X_test) # 1 for inlier (benign), -1 for outlier (attack)
        iso_latency_us = ((time.time() - t0) / len(X_test)) * 1e6
        iso_preds = np.where(raw_iso == -1, 1, 0)
        iso_scores = -iso.score_samples(X_test) # Higher score = more anomalous
        
        results["Isolation_Forest"] = self._compute_binary_metrics(
            y_test, iso_preds, iso_scores, iso_train_time, iso_latency_us, "Isolation Forest"
        )
        self.trained_models["ISO_binary"] = iso

        return results

    def train_evaluate_multiclass(self, X_train: np.ndarray, y_train: np.ndarray,
                                 X_test: np.ndarray, y_test: np.ndarray,
                                 class_names: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Train and evaluate multi-class intrusion detection models:
        Logistic Regression, Random Forest, XGBoost, and LightGBM.
        """
        results = {}

        # 1. Random Forest Multi-class
        print("Training Random Forest (Multi-class)...")
        rf_m = RandomForestClassifier(n_estimators=100, max_depth=16, n_jobs=-1,
                                      random_state=self.random_state, class_weight='balanced')
        t0 = time.time()
        rf_m.fit(X_train, y_train)
        rf_train_time = time.time() - t0
        
        t0 = time.time()
        rf_preds = rf_m.predict(X_test)
        rf_latency_us = ((time.time() - t0) / len(X_test)) * 1e6
        
        results["Random_Forest"] = self._compute_multiclass_metrics(
            y_test, rf_preds, class_names, rf_train_time, rf_latency_us, "Random Forest"
        )
        self.trained_models["RF_multi"] = rf_m

        # 2. XGBoost Multi-class
        print("Training XGBoost (Multi-class)...")
        xgb_m = xgb.XGBClassifier(
            n_estimators=100, max_depth=6, learning_rate=0.1,
            num_class=len(class_names), objective="multi:softprob",
            random_state=self.random_state, eval_metric="mlogloss", n_jobs=-1
        )
        t0 = time.time()
        xgb_m.fit(X_train, y_train)
        xgb_train_time = time.time() - t0
        
        t0 = time.time()
        xgb_preds = xgb_m.predict(X_test)
        xgb_latency_us = ((time.time() - t0) / len(X_test)) * 1e6
        
        results["XGBoost"] = self._compute_multiclass_metrics(
            y_test, xgb_preds, class_names, xgb_train_time, xgb_latency_us, "XGBoost"
        )
        self.trained_models["XGB_multi"] = xgb_m

        # 3. LightGBM Multi-class
        print("Training LightGBM (Multi-class)...")
        lgb_m = lgb.LGBMClassifier(
            n_estimators=100, max_depth=8, learning_rate=0.1,
            random_state=self.random_state, class_weight='balanced', n_jobs=-1, verbose=-1
        )
        t0 = time.time()
        lgb_m.fit(X_train, y_train)
        lgb_train_time = time.time() - t0
        
        t0 = time.time()
        lgb_preds = lgb_m.predict(X_test)
        lgb_latency_us = ((time.time() - t0) / len(X_test)) * 1e6
        
        results["LightGBM"] = self._compute_multiclass_metrics(
            y_test, lgb_preds, class_names, lgb_train_time, lgb_latency_us, "LightGBM"
        )
        self.trained_models["LGB_multi"] = lgb_m

        return results

    def _compute_binary_metrics(self, y_true, y_pred, y_prob, train_time, latency_us, model_name) -> Dict[str, Any]:
        cm = confusion_matrix(y_true, y_pred)
        tn, fp, fn, tp = cm.ravel() if cm.shape == (2, 2) else (0, 0, 0, 0)
        fpr = fp / max(fp + tn, 1)

        try:
            roc = roc_auc_score(y_true, y_prob)
        except Exception:
            roc = 0.5

        try:
            pr_auc = average_precision_score(y_true, y_prob)
        except Exception:
            pr_auc = 0.5

        return {
            "model_name": model_name,
            "accuracy": round(float(np.mean(y_true == y_pred)), 4),
            "precision": round(float(precision_score(y_true, y_pred, zero_division=0)), 4),
            "recall": round(float(recall_score(y_true, y_pred, zero_division=0)), 4),
            "f1_score": round(float(f1_score(y_true, y_pred, zero_division=0)), 4),
            "roc_auc": round(float(roc), 4),
            "pr_auc": round(float(pr_auc), 4),
            "false_positive_rate": round(float(fpr), 4),
            "confusion_matrix": cm.tolist(),
            "train_time_sec": round(train_time, 3),
            "inference_latency_us": round(latency_us, 2)
        }

    def _compute_multiclass_metrics(self, y_true, y_pred, class_names, train_time, latency_us, model_name) -> Dict[str, Any]:
        macro_f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)
        weighted_f1 = f1_score(y_true, y_pred, average="weighted", zero_division=0)
        accuracy = np.mean(y_true == y_pred)
        
        # Per-class metrics
        rep = classification_report(y_true, y_pred, target_names=class_names, output_dict=True, zero_division=0)
        per_class = {}
        for cname in class_names:
            if cname in rep:
                per_class[cname] = {
                    "precision": round(rep[cname]["precision"], 4),
                    "recall": round(rep[cname]["recall"], 4),
                    "f1_score": round(rep[cname]["f1-score"], 4),
                    "support": int(rep[cname]["support"])
                }

        cm = confusion_matrix(y_true, y_pred)

        return {
            "model_name": model_name,
            "accuracy": round(float(accuracy), 4),
            "macro_f1": round(float(macro_f1), 4),
            "weighted_f1": round(float(weighted_f1), 4),
            "per_class": per_class,
            "confusion_matrix": cm.tolist(),
            "train_time_sec": round(train_time, 3),
            "inference_latency_us": round(latency_us, 2)
        }

    def save_model(self, model_key: str, filepath: str):
        """Persist trained model to disk."""
        if model_key in self.trained_models:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            joblib.dump(self.trained_models[model_key], filepath)
            print(f"Saved {model_key} to {filepath}")

if __name__ == "__main__":
    from src.preprocessing.cyber_preprocessor import CyberDataPreprocessor
    preprocessor = CyberDataPreprocessor(random_state=42)
    ton_data = preprocessor.preprocess_ton_iot(sample_size=20000)
    
    suite = CyberModelSuite(random_state=42)
    print("\n--- Evaluating Binary Intrusion Detection (ToN_IoT) ---")
    bin_results = suite.train_evaluate_binary(
        ton_data["X_train"], ton_data["y_bin_train"],
        ton_data["X_test"], ton_data["y_bin_test"]
    )
    for mname, mres in bin_results.items():
        print(f"{mname}: Acc={mres['accuracy']}, F1={mres['f1_score']}, FPR={mres['false_positive_rate']}, ROC-AUC={mres['roc_auc']}, Latency={mres['inference_latency_us']}us")
