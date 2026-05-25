# src/preprocessing.py

import re
import pandas as pd


def normalize_process_number(value):
    """
    Remove caracteres não numéricos do número do processo.
    Isso ajuda a fazer o match entre Benner e DeepLegal.
    """
    if pd.isna(value):
        return None

    value = str(value)
    return re.sub(r"\D", "", value)


def standardize_text(value):
    """
    Padroniza strings para reduzir ruído em categorias.
    """
    if pd.isna(value):
        return None

    value = str(value).strip()

    if value == "":
        return None

    return value.upper()


def create_value_bucket(value):
    """
    Cria faixas de valor ajuizado para usar na similaridade.
    """
    if pd.isna(value):
        return "SEM_VALOR"

    try:
        value = float(value)
    except Exception:
        return "SEM_VALOR"

    if value <= 0:
        return "ZERO_OU_NEGATIVO"
    elif value <= 5_000:
        return "ATE_5K"
    elif value <= 20_000:
        return "5K_20K"
    elif value <= 50_000:
        return "20K_50K"
    elif value <= 100_000:
        return "50K_100K"
    elif value <= 500_000:
        return "100K_500K"
    else:
        return "ACIMA_500K"