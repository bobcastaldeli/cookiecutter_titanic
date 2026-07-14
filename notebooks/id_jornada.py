import pandas as pd
import numpy as np

def criar_id_jornada_pandas(
    df,
    col_cliente="id_cliente",
    col_data="dt_simulacao",
    col_id_simulacao=None,
    horas_gap=24
):
    df = df.copy()

    # Garante datetime
    df[col_data] = pd.to_datetime(df[col_data])

    # Ordenação
    sort_cols = [col_cliente, col_data]
    if col_id_simulacao is not None and col_id_simulacao in df.columns:
        sort_cols.append(col_id_simulacao)

    df = df.sort_values(sort_cols).reset_index(drop=True)

    # Data/hora da simulação anterior dentro do mesmo cliente
    df["dt_simulacao_anterior"] = df.groupby(col_cliente)[col_data].shift(1)

    # Diferença em horas
    df["diff_horas_simulacao_anterior"] = (
        (df[col_data] - df["dt_simulacao_anterior"])
        .dt.total_seconds() / 3600
    )

    # Nova jornada quando:
    # 1. é a primeira simulação do cliente
    # 2. ou o gap é maior que 24h
    df["flag_nova_jornada"] = np.where(
        df["dt_simulacao_anterior"].isna() |
        (df["diff_horas_simulacao_anterior"] > horas_gap),
        1,
        0
    )

    # Número sequencial da jornada dentro do cliente
    df["nr_jornada_cliente"] = df.groupby(col_cliente)["flag_nova_jornada"].cumsum()

    # ID único da jornada
    df["id_jornada"] = (
        df[col_cliente].astype(str)
        + "_J"
        + df["nr_jornada_cliente"].astype(str).str.zfill(4)
    )

    # Ordem da simulação dentro da jornada
    df["ordem_simulacao_jornada"] = (
        df.groupby("id_jornada").cumcount() + 1
    )

    return df
    
def check_pd_na_issues(df, name="df"):
    print(f"\n{name}")
    print("shape:", df.shape)

    # Colunas com pd.NA/nulos
    nulls = df.isna().sum()
    print("\nColunas com nulos:")
    print(nulls[nulls > 0].sort_values(ascending=False).head(30))

    # Dtypes problemáticos
    print("\nDtypes:")
    print(df.dtypes.value_counts())

    print("\nColunas com dtype nullable:")
    nullable_cols = [
        col for col in df.columns
        if str(df[col].dtype) in ["Int64", "Float64", "boolean", "string"]
    ]
    print(nullable_cols[:50])

check_pd_na_issues(df_train, "df_train")
check_pd_na_issues(df_test, "df_test")
check_pd_na_issues(df_oot, "df_oot")

df_train = df_train.replace({pd.NA: np.nan})
df_test = df_test.replace({pd.NA: np.nan})
df_oot = df_oot.replace({pd.NA: np.nan})

for col in categorical_features:
    df_train[col] = df_train[col].astype("object").where(df_train[col].notna(), "MISSING").astype(str)
    df_test[col] = df_test[col].astype("object").where(df_test[col].notna(), "MISSING").astype(str)
    df_oot[col] = df_oot[col].astype("object").where(df_oot[col].notna(), "MISSING").astype(str)

for col in numeric_features:
    df_train[col] = pd.to_numeric(df_train[col], errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(0.0)
    df_test[col] = pd.to_numeric(df_test[col], errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(0.0)
    df_oot[col] = pd.to_numeric(df_oot[col], errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(0.0)

df_train[TARGET_COL] = df_train[TARGET_COL].astype(int)
df_test[TARGET_COL] = df_test[TARGET_COL].astype(int)
df_oot[TARGET_COL] = df_oot[TARGET_COL].astype(int)
