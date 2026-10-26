"""
Cybersecurity Data Preprocessing Pipeline.
Processes ToN_IoT (NetFlow v2) and CICIoT2023 benchmark datasets.
Strictly prevents data leakage: fits transformations only on training partitions.
Implements RobustScaler, removes identity leakage fields (IPs), and produces clean train/test splits.
"""

import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler, LabelEncoder
from typing import Tuple, Dict, Any, List

class CyberDataPreprocessor:
    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.ton_scaler = RobustScaler()
        self.ciciot_scaler = RobustScaler()
        self.ton_label_encoder = LabelEncoder()
        self.ciciot_label_encoder = LabelEncoder()
        self.ton_feature_cols: List[str] = []
        self.ciciot_feature_cols: List[str] = []

    def preprocess_ton_iot(self, raw_csv: str = "data/raw/ton_iot/ton_iot_network.csv",
                           sample_size: int = 60000,
                           test_size: float = 0.2) -> Dict[str, Any]:
        """
        Preprocess ToN_IoT dataset:
        - Drops pure identifier leakage columns (IP strings, DNS query ID)
        - Separates binary target ('Label') and multi-class target ('Attack')
        - Stratified train-test split
        - Robust scaling fit strictly on train split
        """
        print(f"Loading ToN_IoT from {raw_csv}...")
        df = pd.read_csv(raw_csv)
        if sample_size and len(df) > sample_size:
            # Stratified sampling by Attack class to preserve rare attack representation
            df = df.groupby('Attack', group_keys=False).apply(
                lambda x: x.sample(min(len(x), int(np.ceil(sample_size * len(x) / len(df)))),
                                   random_state=self.random_state)
            ).reset_index(drop=True)
            print(f"Stratified subsample to {len(df)} records across all attack classes.")

        # Drop identifiers that cause data leakage
        drop_cols = ["IPV4_SRC_ADDR", "IPV4_DST_ADDR", "DNS_QUERY_ID"]
        feature_df = df.drop(columns=[col for col in drop_cols if col in df.columns])

        # Separate targets
        y_binary = feature_df["Label"].astype(int).values
        y_multi_str = feature_df["Attack"].astype(str).values
        y_multi = self.ton_label_encoder.fit_transform(y_multi_str)

        # Drop targets from features
        X_df = feature_df.drop(columns=["Label", "Attack"])
        # Fill any remaining NaNs or Infs
        X_df = X_df.replace([np.inf, -np.inf], np.nan).fillna(0)

        self.ton_feature_cols = list(X_df.columns)

        # Stratified train/test split on multi-class labels to maintain rare attacks in both
        X_train, X_test, y_bin_train, y_bin_test, y_mul_train, y_mul_test = train_test_split(
            X_df.values, y_binary, y_multi, test_size=test_size, random_state=self.random_state, stratify=y_multi
        )

        # Fit RobustScaler ONLY on training data
        X_train_scaled = self.ton_scaler.fit_transform(X_train)
        X_test_scaled = self.ton_scaler.transform(X_test)

        os.makedirs("data/processed/ton_iot", exist_ok=True)
        # Save feature column list and label mappings
        label_mapping = {int(idx): str(cls_name) for idx, cls_name in enumerate(self.ton_label_encoder.classes_)}
        
        return {
            "X_train": X_train_scaled,
            "X_test": X_test_scaled,
            "y_bin_train": y_bin_train,
            "y_bin_test": y_bin_test,
            "y_mul_train": y_mul_train,
            "y_mul_test": y_mul_test,
            "feature_names": self.ton_feature_cols,
            "label_mapping": label_mapping,
            "class_names": list(self.ton_label_encoder.classes_)
        }

    def preprocess_ciciot2023(self, raw_csv: str = "data/raw/ciciot2023/ciciot2023_benchmark.csv",
                              sample_size: int = 40000,
                              test_size: float = 0.2) -> Dict[str, Any]:
        """
        Preprocess CICIoT2023 dataset:
        - Drops non-feature columns
        - Stratified train-test split
        - Robust scaling fit strictly on train split
        """
        print(f"Loading CICIoT2023 from {raw_csv}...")
        df = pd.read_csv(raw_csv)
        if sample_size and len(df) > sample_size:
            df = df.groupby('label', group_keys=False).apply(
                lambda x: x.sample(min(len(x), sample_size // df['label'].nunique()), random_state=self.random_state)
            ).reset_index(drop=True)
            print(f"Balanced subsample to {len(df)} records.")

        y_multi_str = df["label"].astype(str).values
        y_multi = self.ciciot_label_encoder.fit_transform(y_multi_str)
        y_binary = (df["label"] != "Benign").astype(int).values

        X_df = df.drop(columns=["label"])
        X_df = X_df.replace([np.inf, -np.inf], np.nan).fillna(0)
        self.ciciot_feature_cols = list(X_df.columns)

        X_train, X_test, y_bin_train, y_bin_test, y_mul_train, y_mul_test = train_test_split(
            X_df.values, y_binary, y_multi, test_size=test_size, random_state=self.random_state, stratify=y_multi
        )

        X_train_scaled = self.ciciot_scaler.fit_transform(X_train)
        X_test_scaled = self.ciciot_scaler.transform(X_test)

        os.makedirs("data/processed/ciciot2023", exist_ok=True)
        label_mapping = {int(idx): str(cls_name) for idx, cls_name in enumerate(self.ciciot_label_encoder.classes_)}

        return {
            "X_train": X_train_scaled,
            "X_test": X_test_scaled,
            "y_bin_train": y_bin_train,
            "y_bin_test": y_bin_test,
            "y_mul_train": y_mul_train,
            "y_mul_test": y_mul_test,
            "feature_names": self.ciciot_feature_cols,
            "label_mapping": label_mapping,
            "class_names": list(self.ciciot_label_encoder.classes_)
        }

if __name__ == "__main__":
    preprocessor = CyberDataPreprocessor(random_state=42)
    ton_data = preprocessor.preprocess_ton_iot(sample_size=30000)
    print("ToN_IoT processed:")
    print("  Train shape:", ton_data["X_train"].shape)
    print("  Test shape:", ton_data["X_test"].shape)
    print("  Classes:", ton_data["class_names"])
    
    ciciot_data = preprocessor.preprocess_ciciot2023(sample_size=20000)
    print("\nCICIoT2023 processed:")
    print("  Train shape:", ciciot_data["X_train"].shape)
    print("  Test shape:", ciciot_data["X_test"].shape)
    print("  Classes:", ciciot_data["class_names"])
