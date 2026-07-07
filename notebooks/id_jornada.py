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