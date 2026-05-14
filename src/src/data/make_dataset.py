from pathlib import Path

import pandas as pd

from config import get_project_root, load_params


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
        .str.replace("/", "_", regex=False)
    )
    return df


def validate_raw_data(df: pd.DataFrame) -> None:
    required_columns = {
        "survived",
        "pclass",
        "sex",
        "age",
        "sibsp",
        "parch",
        "fare",
        "embarked",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(f"Colunas obrigatórias ausentes: {missing_columns}")

    if df.empty:
        raise ValueError("Dataset bruto está vazio.")

    if df["survived"].isna().any():
        raise ValueError("A coluna target 'survived' possui valores nulos.")


def make_dataset() -> None:
    params = load_params()
    project_root = get_project_root()

    raw_path = project_root / params["data"]["raw_path"]
    processed_path = project_root / params["data"]["processed_path"]

    df = pd.read_csv(raw_path)
    df = normalize_column_names(df)

    selected_columns = [
        "survived",
        "pclass",
        "sex",
        "age",
        "sibsp",
        "parch",
        "fare",
        "embarked",
    ]

    df = df[selected_columns]

    validate_raw_data(df)

    processed_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(processed_path, index=False)

    print(f"Dataset processado salvo em: {processed_path}")
    print(f"Shape: {df.shape}")


if __name__ == "__main__":
    make_dataset()