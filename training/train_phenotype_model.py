"""Train a compact phenotype probability model and export it for Node.js inference.

The original AI server trains a large ensemble at startup. That is useful for
experimentation, but it is too slow and dependency-heavy for a Vercel request.
This script trains once from the project dataset and exports only the scaler
and neural-network weights needed by the production API.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / "ai" / "final_merged_3.csv"
MODEL_PATH = ROOT / "model" / "phenotype-model.json"

TARGET_GROUPS = {
    "eye": {
        "blue": "PBlueEye",
        "intermediate": "PIntermediateEye",
        "brown": "PBrownEye",
    },
    "hair": {
        "blonde": "PBlondHair",
        "brown": "PBrownHair",
        "red": "PRedHair",
        "black": "PBlackHair",
    },
    "skin": {
        "veryPale": "PVeryPaleSkin",
        "pale": "PPaleSkin",
        "intermediate": "PIntermediateSkin",
        "dark": "PDarkSkin",
        "darkToBlack": "PDarktoBlackSkin",
    },
}


def make_model() -> MLPRegressor:
    return MLPRegressor(
        hidden_layer_sizes=(96, 48),
        activation="relu",
        solver="adam",
        alpha=0.0003,
        batch_size=128,
        learning_rate_init=0.002,
        max_iter=300,
        early_stopping=True,
        validation_fraction=0.12,
        n_iter_no_change=20,
        random_state=42,
    )


def normalized_groups(values: np.ndarray) -> np.ndarray:
    normalized = np.zeros_like(values)
    offset = 0
    for group in TARGET_GROUPS.values():
        width = len(group)
        block = np.clip(values[:, offset : offset + width], 0, None)
        normalized[:, offset : offset + width] = block / np.maximum(
            block.sum(axis=1, keepdims=True), 1e-12
        )
        offset += width
    return normalized


def rounded(value):
    return np.asarray(value).round(10).tolist()


def main() -> None:
    df = pd.read_csv(DATASET_PATH)
    features = [column for column in df.columns if column.startswith("rs")]
    target_columns = [
        column for group in TARGET_GROUPS.values() for column in group.values()
    ]

    x = df[features].to_numpy(dtype=float)
    y = df[target_columns].to_numpy(dtype=float)
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42
    )

    eval_imputer = SimpleImputer(strategy="median")
    eval_scaler = StandardScaler()
    x_train_scaled = eval_scaler.fit_transform(eval_imputer.fit_transform(x_train))
    x_test_scaled = eval_scaler.transform(eval_imputer.transform(x_test))
    eval_model = make_model()
    eval_model.fit(x_train_scaled, y_train)
    predictions = normalized_groups(eval_model.predict(x_test_scaled))

    metrics = {"overall_mae": round(float(mean_absolute_error(y_test, predictions)), 6)}
    offset = 0
    for trait, group in TARGET_GROUPS.items():
        width = len(group)
        truth = y_test[:, offset : offset + width]
        predicted = predictions[:, offset : offset + width]
        metrics[trait] = {
            "mae": round(float(mean_absolute_error(truth, predicted)), 6),
            "top_class_accuracy": round(
                float(np.mean(np.argmax(truth, axis=1) == np.argmax(predicted, axis=1))),
                6,
            ),
        }
        offset += width

    imputer = SimpleImputer(strategy="median")
    scaler = StandardScaler()
    x_scaled = scaler.fit_transform(imputer.fit_transform(x))
    model = make_model()
    model.fit(x_scaled, y)

    artifact = {
        "format_version": 1,
        "model_type": "standard_scaler_mlp_regressor",
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "training_rows": int(len(df)),
        "features": features,
        "target_groups": {
            trait: list(group.keys()) for trait, group in TARGET_GROUPS.items()
        },
        "imputer_median": rounded(imputer.statistics_),
        "scaler_mean": rounded(scaler.mean_),
        "scaler_scale": rounded(scaler.scale_),
        "layers": [
            {"weights": rounded(weights), "biases": rounded(biases)}
            for weights, biases in zip(model.coefs_, model.intercepts_)
        ],
        "metrics": metrics,
    }

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    MODEL_PATH.write_text(json.dumps(artifact, separators=(",", ":")), encoding="utf-8")
    print(f"Exported {MODEL_PATH.relative_to(ROOT)} ({MODEL_PATH.stat().st_size:,} bytes)")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
