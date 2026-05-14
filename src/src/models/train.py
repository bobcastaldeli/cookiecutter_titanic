import os
import pickle
from pathlib import Path

import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_auc_score

from modelo_titanic.config import get_project_root, load_params


def train_model() -> None:
    params = load_params()
    project_root = get_project_root()

    train_path = project_root / params["data"]["train_path"]
    model_path = project_root / params["model"]["model_path"]

    target_column = params["model"]["target_column"]

    train_df = pd.read_parquet(train_path)

    X_train = train_df.drop(columns=[target_column])
    y_train = train_df[target_column]

    model = RandomForestClassifier(
        n_estimators=params["training"]["n_estimators"],
        max_depth=params["training"]["max_depth"],
        min_samples_leaf=params["training"]["min_samples_leaf"],
        random_state=params["model"]["random_state"],
        n_jobs=-1,
    )

    mlflow_tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "file:./mlruns")
    mlflow_experiment_name = os.getenv(
        "MLFLOW_EXPERIMENT_NAME",
        params["project"]["experiment_name"],
    )

    mlflow.set_tracking_uri(mlflow_tracking_uri)
    mlflow.set_experiment(mlflow_experiment_name)

    with mlflow.start_run(run_name="train_random_forest"):
        mlflow.log_param("model_type", "RandomForestClassifier")
        mlflow.log_params(params["training"])
        mlflow.log_param("target_column", target_column)
        mlflow.log_param("train_path", str(train_path))

        model.fit(X_train, y_train)

        y_train_pred = model.predict(X_train)
        y_train_score = model.predict_proba(X_train)[:, 1]

        train_accuracy = accuracy_score(y_train, y_train_pred)
        train_roc_auc = roc_auc_score(y_train, y_train_score)

        mlflow.log_metric("train_accuracy", train_accuracy)
        mlflow.log_metric("train_roc_auc", train_roc_auc)

        model_path.parent.mkdir(parents=True, exist_ok=True)

        with open(model_path, "wb") as file:
            pickle.dump(model, file)

        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
        )

        print(f"Modelo salvo em: {model_path}")
        print(f"Train accuracy: {train_accuracy:.4f}")
        print(f"Train ROC AUC: {train_roc_auc:.4f}")


if __name__ == "__main__":
    train_model()