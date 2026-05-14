import json
import os
import pickle
from pathlib import Path

import matplotlib.pyplot as plt
import mlflow
import pandas as pd
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from modelo_titanic.config import get_project_root, load_params


def save_json(data: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def plot_confusion_matrix(model, X_test, y_test, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(6, 6))
    ConfusionMatrixDisplay.from_estimator(model, X_test, y_test, ax=ax)
    ax.set_title("Confusion Matrix")

    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def plot_feature_importance(model, feature_names: list[str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    importances = pd.DataFrame(
        {
            "feature": feature_names,
            "importance": model.feature_importances_,
        }
    ).sort_values("importance", ascending=True)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(importances["feature"], importances["importance"])
    ax.set_title("Feature Importance")
    ax.set_xlabel("Importance")

    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def evaluate_model() -> None:
    params = load_params()
    project_root = get_project_root()

    test_path = project_root / params["data"]["test_path"]
    model_path = project_root / params["model"]["model_path"]

    metrics_path = project_root / params["reports"]["metrics_path"]
    classification_report_path = project_root / params["reports"]["classification_report_path"]
    confusion_matrix_path = project_root / params["reports"]["confusion_matrix_path"]
    feature_importance_path = project_root / params["reports"]["feature_importance_path"]

    target_column = params["model"]["target_column"]

    test_df = pd.read_parquet(test_path)

    X_test = test_df.drop(columns=[target_column])
    y_test = test_df[target_column]

    with open(model_path, "rb") as file:
        model = pickle.load(file)

    y_pred = model.predict(X_test)
    y_score = model.predict_proba(X_test)[:, 1]

    metrics = {
        "test_accuracy": float(accuracy_score(y_test, y_pred)),
        "test_precision": float(precision_score(y_test, y_pred)),
        "test_recall": float(recall_score(y_test, y_pred)),
        "test_f1": float(f1_score(y_test, y_pred)),
        "test_roc_auc": float(roc_auc_score(y_test, y_score)),
    }

    report = classification_report(y_test, y_pred, output_dict=True)

    save_json(metrics, metrics_path)
    save_json(report, classification_report_path)

    plot_confusion_matrix(model, X_test, y_test, confusion_matrix_path)
    plot_feature_importance(model, list(X_test.columns), feature_importance_path)

    mlflow_tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "file:./mlruns")
    mlflow_experiment_name = os.getenv(
        "MLFLOW_EXPERIMENT_NAME",
        params["project"]["experiment_name"],
    )

    mlflow.set_tracking_uri(mlflow_tracking_uri)
    mlflow.set_experiment(mlflow_experiment_name)

    with mlflow.start_run(run_name="evaluate_random_forest"):
        mlflow.log_metrics(metrics)
        mlflow.log_artifact(str(metrics_path))
        mlflow.log_artifact(str(classification_report_path))
        mlflow.log_artifact(str(confusion_matrix_path))
        mlflow.log_artifact(str(feature_importance_path))

    print("Métricas de teste:")
    for metric_name, metric_value in metrics.items():
        print(f"{metric_name}: {metric_value:.4f}")


if __name__ == "__main__":
    evaluate_model()