import pandas as pd
from sklearn.model_selection import train_test_split

from modelo_titanic.config import get_project_root, load_params


def build_features_from_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["age"] = df["age"].fillna(df["age"].median())
    df["fare"] = df["fare"].fillna(df["fare"].median())
    df["embarked"] = df["embarked"].fillna("unknown")

    df["family_size"] = df["sibsp"] + df["parch"] + 1
    df["is_alone"] = (df["family_size"] == 1).astype(int)

    df["sex_male"] = (df["sex"] == "male").astype(int)

    embarked_dummies = pd.get_dummies(
        df["embarked"],
        prefix="embarked",
        dummy_na=False,
    )

    df = pd.concat([df, embarked_dummies], axis=1)

    columns_to_drop = ["sex", "embarked"]
    df = df.drop(columns=columns_to_drop)

    return df


def build_features() -> None:
    params = load_params()
    project_root = get_project_root()

    processed_path = project_root / params["data"]["processed_path"]
    features_path = project_root / params["data"]["features_path"]
    train_path = project_root / params["data"]["train_path"]
    test_path = project_root / params["data"]["test_path"]

    target_column = params["model"]["target_column"]

    df = pd.read_parquet(processed_path)
    df_features = build_features_from_dataframe(df)

    train_df, test_df = train_test_split(
        df_features,
        test_size=params["model"]["test_size"],
        random_state=params["model"]["random_state"],
        stratify=df_features[target_column],
    )

    features_path.parent.mkdir(parents=True, exist_ok=True)

    df_features.to_parquet(features_path, index=False)
    train_df.to_parquet(train_path, index=False)
    test_df.to_parquet(test_path, index=False)

    print(f"Features salvas em: {features_path}")
    print(f"Treino salvo em: {train_path}")
    print(f"Teste salvo em: {test_path}")
    print(f"Shape features: {df_features.shape}")
    print(f"Shape treino: {train_df.shape}")
    print(f"Shape teste: {test_df.shape}")


if __name__ == "__main__":
    build_features()