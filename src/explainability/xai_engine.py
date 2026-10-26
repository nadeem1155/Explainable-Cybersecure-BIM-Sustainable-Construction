"""
Explainable AI (XAI) Engine.
Implements TreeSHAP for interpreting machine learning cybersecurity alerts
and multi-objective sustainable construction trade-offs.
Computes global feature attributions, local flow explanations, and explanation stability (RBO).
"""

import os
import shap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List, Any, Tuple, Optional

class ExplainableAIEngine:
    def __init__(self, model, feature_names: List[str]):
        self.model = model
        self.feature_names = feature_names
        # Initialize TreeExplainer
        self.explainer = shap.TreeExplainer(model)

    def compute_global_attributions(self, X_sample: np.ndarray, max_display: int = 15) -> Dict[str, Any]:
        """Compute global mean absolute SHAP attributions across feature set."""
        # Calculate SHAP values
        shap_values = self.explainer.shap_values(X_sample)
        if isinstance(shap_values, list):
            # For multi-class or list output, average across classes or use positive class
            sv = np.array(shap_values[1]) if len(shap_values) == 2 else np.mean(np.abs(np.array(shap_values)), axis=0)
        elif len(shap_values.shape) == 3:
            sv = np.mean(np.abs(shap_values), axis=2)
        else:
            sv = shap_values

        mean_abs_shap = np.mean(np.abs(sv), axis=0)
        sorted_indices = np.argsort(mean_abs_shap)[::-1]

        ranked_features = []
        for rank, idx in enumerate(sorted_indices[:max_display]):
            ranked_features.append({
                "rank": rank + 1,
                "feature": self.feature_names[idx],
                "mean_abs_shap": round(float(mean_abs_shap[idx]), 5)
            })

        return {
            "top_features": ranked_features,
            "all_mean_abs_shap": {self.feature_names[i]: float(mean_abs_shap[i]) for i in range(len(self.feature_names))},
            "raw_shap_sample": sv[:100]
        }

    def explain_single_flow(self, x_flow: np.ndarray, predicted_class: str,
                           confidence: float) -> Dict[str, Any]:
        """Generate local feature attributions for a single network flow or security event."""
        x_reshaped = x_flow.reshape(1, -1)
        sv = self.explainer.shap_values(x_reshaped)
        if isinstance(sv, list):
            sv_flow = sv[1][0] if len(sv) == 2 else sv[0][0]
        elif len(sv.shape) == 3:
            sv_flow = sv[0, :, 1] if sv.shape[2] > 1 else sv[0, :, 0]
        else:
            sv_flow = sv[0]

        top_indices = np.argsort(np.abs(sv_flow))[::-1][:8]
        top_contributions = []
        for idx in top_indices:
            top_contributions.append({
                "feature": self.feature_names[idx],
                "feature_value": float(x_flow[idx]),
                "shap_impact": round(float(sv_flow[idx]), 5),
                "direction": "Pushes toward Attack" if sv_flow[idx] > 0 else "Pushes toward Benign"
            })

        base_val = float(self.explainer.expected_value[1] if isinstance(self.explainer.expected_value, (list, np.ndarray)) else self.explainer.expected_value)

        return {
            "predicted_class": predicted_class,
            "confidence": round(float(confidence), 4),
            "base_value": round(base_val, 4),
            "top_contributions": top_contributions
        }

    def evaluate_explanation_stability_rbo(self, X_eval: np.ndarray, n_splits: int = 5,
                                           p: float = 0.9) -> Dict[str, float]:
        """
        Evaluate Rank-Biased Overlap (RBO) stability of feature attributions across subsamples.
        Grounded in metric requirements of Section 10 and Hypothesis H4.
        """
        rankings = []
        sub_size = len(X_eval) // n_splits
        for i in range(n_splits):
            sub_X = X_eval[i*sub_size : (i+1)*sub_size]
            attr = self.compute_global_attributions(sub_X, max_display=10)
            rankings.append([item["feature"] for item in attr["top_features"]])

        def rbo(list1, list2, p=0.9):
            """Calculate Rank-Biased Overlap between two ranked lists."""
            k = min(len(list1), len(list2))
            s1, s2 = set(), set()
            rbo_val = 0.0
            for d in range(1, k + 1):
                s1.add(list1[d-1])
                s2.add(list2[d-1])
                overlap = len(s1.intersection(s2))
                agreement = overlap / d
                rbo_val += (1.0 - p) * (p**(d - 1)) * agreement
            rbo_val += (p**k) * (len(s1.intersection(s2)) / k)
            return rbo_val

        rbo_scores = []
        for i in range(len(rankings)):
            for j in range(i + 1, len(rankings)):
                score = rbo(rankings[i], rankings[j], p=p)
                rbo_scores.append(score)

        mean_rbo = float(np.mean(rbo_scores))
        std_rbo = float(np.std(rbo_scores))

        return {
            "mean_rbo_stability": round(mean_rbo, 4),
            "std_rbo_stability": round(std_rbo, 4),
            "is_stable_h4": bool(mean_rbo >= 0.85)
        }

    @staticmethod
    def explain_design_alternatives_tradeoffs(alternatives: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Explain the engineering and physical mechanics driving the differences
        among Carbon-Oriented, Cost-Oriented, and Balanced design alternatives.
        """
        c_alt = alternatives.get("carbon_oriented", {})
        l_alt = alternatives.get("cost_oriented", {})
        b_alt = alternatives.get("balanced", {})

        c_carb = c_alt.get("embodied_carbon_kgCO2eq", 0)
        l_carb = l_alt.get("embodied_carbon_kgCO2eq", 0)
        b_carb = b_alt.get("embodied_carbon_kgCO2eq", 0)

        c_cost = c_alt.get("lifecycle_cost_npv_inr", 0)
        l_cost = l_alt.get("lifecycle_cost_npv_inr", 0)
        b_cost = b_alt.get("lifecycle_cost_npv_inr", 0)

        carbon_savings_pct = round(((l_carb - c_carb) / max(l_carb, 1)) * 100.0, 2)
        cost_savings_pct = round(((c_cost - l_cost) / max(c_cost, 1)) * 100.0, 2)

        explanation = {
            "carbon_reduction_delta_pct": carbon_savings_pct,
            "cost_difference_delta_pct": cost_savings_pct,
            "carbon_oriented_driver": (
                f"Adopts {c_alt.get('beam_material')} and {c_alt.get('rebar_material')}, "
                f"which drastically curtails cradle-to-gate GWP emissions by replacing virgin blast-furnace steel with recycled EAF."
            ),
            "cost_oriented_driver": (
                f"Leverages {l_alt.get('wall_material')} and {l_alt.get('beam_material')}, "
                f"achieving lowest upfront capital expenditure based on CPWD schedule rates while maintaining DCR <= 1.0."
            ),
            "balanced_compromise": (
                f"Employs {b_alt.get('beam_material')} with {b_alt.get('wall_material')}, "
                f"achieving {round(b_carb, 1)} kg CO2 eq and INR {round(b_cost, 2)} NPV, balancing social carbon cost and budget."
            )
        }
        return explanation

if __name__ == "__main__":
    from src.preprocessing.cyber_preprocessor import CyberDataPreprocessor
    from src.models.cyber_models import CyberModelSuite

    prep = CyberDataPreprocessor(random_state=42)
    ton = prep.preprocess_ton_iot(sample_size=10000)
    suite = CyberModelSuite(random_state=42)
    suite.train_evaluate_binary(ton["X_train"], ton["y_bin_train"], ton["X_test"], ton["y_bin_test"])
    
    xgb_model = suite.trained_models["XGB_binary"]
    xai = ExplainableAIEngine(xgb_model, ton["feature_names"])
    
    print("\n--- Computing Global TreeSHAP Attributions ---")
    glob_attr = xai.compute_global_attributions(ton["X_test"][:300])
    for item in glob_attr["top_features"][:7]:
        print(f"Rank {item['rank']}: {item['feature']} (mean |SHAP| = {item['mean_abs_shap']})")

    print("\n--- Evaluating Explanation Stability (RBO) ---")
    stability = xai.evaluate_explanation_stability_rbo(ton["X_test"][:500], n_splits=4)
    print(f"Mean RBO: {stability['mean_rbo_stability']} (H4 Verified: {stability['is_stable_h4']})")
