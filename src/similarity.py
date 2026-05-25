# src/similarity.py

import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics.pairwise import cosine_similarity
from src.config import SIMILARITY_FEATURES


def prepare_similarity_matrix(df):
    """
    Cria matriz one-hot para similaridade estrutural.
    """
    features = [col for col in SIMILARITY_FEATURES if col in df.columns]

    if "valor_ajuizado_bucket" in df.columns:
        features.append("valor_ajuizado_bucket")

    if not features:
        raise ValueError("Nenhuma feature de similaridade encontrada.")

    base = df[["process_number_norm"] + features].copy()
    base = base.dropna(subset=["process_number_norm"])
    base = base.drop_duplicates(subset=["process_number_norm"])

    for col in features:
        base[col] = base[col].fillna("DESCONHECIDO").astype(str)

    encoder = OneHotEncoder(handle_unknown="ignore")
    X = encoder.fit_transform(base[features])

    return base, X, features


def get_similar_cases(df, target_process_number_norm, top_n=10):
    """
    Retorna processos similares com base em atributos categóricos.
    """
    base, X, features = prepare_similarity_matrix(df)

    target_idx = base.index[base["process_number_norm"] == target_process_number_norm].tolist()

    if not target_idx:
        return pd.DataFrame()

    # Como o índice original pode não ser sequencial após drop_duplicates,
    # vamos resetar para usar posição corretamente.
    base = base.reset_index(drop=True)
    base, X, features = prepare_similarity_matrix(
        df.drop_duplicates(subset=["process_number_norm"]).reset_index(drop=True)
    )

    target_pos = base.index[base["process_number_norm"] == target_process_number_norm].tolist()

    if not target_pos:
        return pd.DataFrame()

    target_pos = target_pos[0]

    sims = cosine_similarity(X[target_pos], X).flatten()

    result = base.copy()
    result["similarity_score"] = sims

    result = result[result["process_number_norm"] != target_process_number_norm]
    result = result.sort_values("similarity_score", ascending=False).head(top_n)

    return result


def explain_similarity(target_row, candidate_row, features):
    """
    Explica motivos simples de similaridade.
    """
    reasons = []

    for feature in features:
        if feature not in target_row.index or feature not in candidate_row.index:
            continue

        if pd.notna(target_row[feature]) and target_row[feature] == candidate_row[feature]:
            reasons.append(feature)

    return reasons