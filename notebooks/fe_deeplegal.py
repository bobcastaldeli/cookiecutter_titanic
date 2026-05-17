from pathlib import Path
import zipfile, textwrap, os, json

base = Path("/mnt/data/feature_engineering_juridico_modules")
src = base / "src" / "feature_engineering"
base.mkdir(parents=True, exist_ok=True)
src.mkdir(parents=True, exist_ok=True)

files = {}

files["src/feature_engineering/__init__.py"] = '''"""
Módulos de feature engineering jurídico.

Uso típico em notebook:

from src.feature_engineering.config import *
from src.feature_engineering.value_features import add_value_features
from src.feature_engineering.date_features import add_main_date_features
from src.feature_engineering.event_features import add_event_ratio_features, add_event_complexity_features
from src.feature_engineering.entity_features import add_list_entity_features
from src.feature_engineering.target_encoding import add_smooth_target_rate_features
from src.feature_engineering.leakage import identify_leakage_columns, remove_leakage_columns
from src.feature_engineering.feature_selection import build_feature_candidate_report
"""
'''

files["src/feature_engineering/config.py"] = '''"""
Configurações centrais para feature engineering jurídico.
Ajuste aqui os nomes de colunas conforme seu ambiente.
"""

from pathlib import Path

BASE_DIR = Path(".")
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"
REPORTS_DIR = BASE_DIR / "outputs" / "reports"

for path in [RAW_DIR, INTERIM_DIR, PROCESSED_DIR, REPORTS_DIR]:
    path.mkdir(parents=True, exist_ok=True)

PROCESS_ID_COL = "numero_processo"
TARGET_COL = "perda_banco"

# Colunas de eventos, caso use a base de eventos tratada
EVENT_NUM_COL = "numero"
EVENT_TYPE_COL = "tipo"
EVENT_TEXT_COL = "texto"
EVENT_DATE_COL = "data"
EVENT_CATEGORY_COL = "tipo_categoria"

# Datas principais na ABT/base de processos
MAIN_DATE_COLS = [
    "data_distribuicao_data",
    "primeiromovimento_data",
    "data_ultimo_movimento_data",
    "ultimomovimento_data",
    "data_primeiro_evento",
    "data_ultimo_evento",
]

# Coluna de valor mais segura para feature inicial
MAIN_VALUE_COL = "valor_valor"

# Colunas com listas/entidades
LIST_ENTITY_COLS = [
    "adv_requerente_lista",
    "adv_requerido_lista",
    "requerente_lista",
    "requerido_lista",
]

# Colunas para target encoding suavizado exploratório
GROUP_COLS_FOR_ENCODING = [
    "assunto_normalizado_texto",
    "assunto_texto",
    "classe_texto",
    "area_texto",
    "uf",
    "cidade",
    "vara_texto",
    "orgao_julgador_texto",
    "juiz_normalizado_texto",
    "fase_processual_texto",
    "status_texto",
    "tipo_de_justica_texto",
    "tipo_de_processo_texto",
    "tipo_de_requerente_texto",
    "tipo_de_requerido_texto",
    "escritorio_cna_requerente_texto",
    "escritorio_cna_requerido_texto",
    "primeiro_adv_requerente_lista",
    "primeiro_adv_requerido_lista",
    "ultima_categoria_evento",
    "penultima_categoria_evento",
]

RECENT_WINDOWS = [30, 60, 90, 180, 365]
'''

files["src/feature_engineering/utils.py"] = '''"""
Funções utilitárias reutilizáveis.
"""

import re
import unicodedata
import numpy as np
import pandas as pd


NULL_STRINGS = {"", "null", "nan", "none", "na", "n/a", "-"}


def normalize_text(text):
    """
    Normaliza texto:
    - lowercase
    - remove acentos
    - remove caracteres especiais
    - remove múltiplos espaços
    - converte strings nulas para None
    """
    if pd.isna(text):
        return None

    text = str(text).strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^a-z0-9\\s]", " ", text)
    text = re.sub(r"\\s+", " ", text).strip()

    if text in NULL_STRINGS:
        return None

    return text


def safe_divide(a, b):
    """
    Divisão segura para arrays/séries, retornando NaN se denominador for zero/nulo.
    """
    return np.where((b == 0) | pd.isna(b), np.nan, a / b)


def sanitize_column_name(name):
    """
    Sanitiza nome de coluna para uso em features.
    """
    name = str(name)
    name = normalize_text(name) or "unknown"
    name = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    name = re.sub(r"_+", "_", name).strip("_")
    return name


def ensure_columns_exist(df, cols, raise_error=False):
    """
    Retorna apenas colunas existentes e, opcionalmente, lança erro se alguma faltar.
    """
    existing = [c for c in cols if c in df.columns]
    missing = [c for c in cols if c not in df.columns]

    if missing and raise_error:
        raise KeyError(f"Colunas ausentes: {missing}")

    return existing, missing
'''

files["src/feature_engineering/value_features.py"] = '''"""
Features financeiras/de valor.

Atenção:
- valor_valor costuma ser uma feature inicial segura.
- condenacao_valor, valor_arbitrado_valor e valor_do_acordo_valor podem vazar resultado.
"""

import numpy as np
import pandas as pd


def profile_value_columns(df, output_path=None):
    """
    Identifica e resume colunas relacionadas a valores financeiros.
    """
    value_cols = [
        c for c in df.columns
        if any(term in c.lower() for term in ["valor", "vl", "honorario", "multa"])
    ]

    rows = []

    for col in value_cols:
        s = pd.to_numeric(df[col], errors="coerce")
        rows.append({
            "coluna": col,
            "qtd_nao_nulos": int(s.notna().sum()),
            "perc_nao_nulos": float(s.notna().mean()),
            "media": s.mean(),
            "mediana": s.median(),
            "p95": s.quantile(0.95),
            "max": s.max()
        })

    report = pd.DataFrame(rows).sort_values("perc_nao_nulos", ascending=False)

    if output_path:
        report.to_csv(output_path, index=False)

    return report


def add_value_features(df, value_col="valor_valor"):
    """
    Cria features a partir da coluna principal de valor.

    Features:
    - valor_is_null
    - valor_log1p
    - valor_zero_ou_nulo
    - valor_faixa_q
    """
    df = df.copy()

    if value_col not in df.columns:
        print(f"[WARN] Coluna {value_col} não encontrada. Nenhuma feature de valor criada.")
        return df

    df[value_col] = pd.to_numeric(df[value_col], errors="coerce")

    df[f"{value_col}_is_null"] = df[value_col].isna().astype(int)

    df[f"{value_col}_log1p"] = np.where(
        df[value_col].fillna(0) > 0,
        np.log1p(df[value_col]),
        0
    )

    df[f"{value_col}_zero_ou_nulo"] = (
        df[value_col].isna() | (df[value_col] <= 0)
    ).astype(int)

    try:
        df[f"{value_col}_faixa_q"] = pd.qcut(
            df[value_col],
            q=5,
            duplicates="drop"
        ).astype(str)
    except Exception:
        df[f"{value_col}_faixa_q"] = "sem_faixa"

    return df
'''

files["src/feature_engineering/date_features.py"] = '''"""
Features de data e safra.
"""

import pandas as pd
import numpy as np


def infer_reference_date(df, candidate_cols=None):
    """
    Infere uma data de referência usando a maior data entre colunas candidatas.
    """
    if candidate_cols is None:
        candidate_cols = [
            "data_ultimo_evento",
            "data_ultimo_movimento_data",
            "ultimomovimento_data",
            "modified"
        ]

    dates = []

    for col in candidate_cols:
        if col in df.columns:
            s = pd.to_datetime(df[col], errors="coerce")
            max_date = s.max()
            if pd.notna(max_date):
                dates.append(max_date)

    if not dates:
        return pd.Timestamp.today().normalize()

    return max(dates)


def add_date_features(df, date_col):
    """
    Cria features de calendário para uma coluna de data.
    """
    df = df.copy()

    if date_col not in df.columns:
        return df

    s = pd.to_datetime(df[date_col], errors="coerce")
    df[date_col] = s

    df[f"{date_col}_ano"] = s.dt.year
    df[f"{date_col}_mes"] = s.dt.month
    df[f"{date_col}_trimestre"] = s.dt.quarter
    df[f"{date_col}_ano_mes"] = s.dt.to_period("M").astype(str)
    df[f"{date_col}_is_null"] = s.isna().astype(int)

    return df


def add_age_feature(df, start_date_col, data_ref):
    """
    Cria idade em dias e anos desde uma data até data_ref.
    """
    df = df.copy()

    if start_date_col not in df.columns:
        return df

    s = pd.to_datetime(df[start_date_col], errors="coerce")
    df[start_date_col] = s

    df[f"idade_desde_{start_date_col}_dias"] = (data_ref - s).dt.days
    df[f"idade_desde_{start_date_col}_anos"] = df[f"idade_desde_{start_date_col}_dias"] / 365.25

    return df


def add_main_date_features(df, main_date_cols=None, data_ref=None):
    """
    Aplica features de data nas principais datas e cria idades.
    """
    df = df.copy()

    if main_date_cols is None:
        main_date_cols = [
            "data_distribuicao_data",
            "primeiromovimento_data",
            "data_ultimo_movimento_data",
            "ultimomovimento_data",
            "data_primeiro_evento",
            "data_ultimo_evento",
        ]

    main_date_cols = [c for c in main_date_cols if c in df.columns]

    for col in main_date_cols:
        df = add_date_features(df, col)

    if data_ref is None:
        data_ref = infer_reference_date(df)

    for col in ["data_distribuicao_data", "primeiromovimento_data", "data_primeiro_evento"]:
        if col in df.columns:
            df = add_age_feature(df, col, data_ref)

    return df, data_ref
'''

files["src/feature_engineering/event_features.py"] = '''"""
Features derivadas da trajetória de eventos processuais.

Parte dessas funções usa a ABT já gerada pela EDA.
Outras usam a base de eventos tratada.
"""

import re
import numpy as np
import pandas as pd
from .utils import safe_divide


def add_event_ratio_features(df):
    """
    Cria proporções das categorias de evento:
    qtd_evento_cat_X / qtd_eventos
    """
    df = df.copy()

    if "qtd_eventos" not in df.columns:
        print("[WARN] qtd_eventos não encontrada. Pulando proporções de eventos.")
        return df

    event_count_cols = [
        c for c in df.columns
        if c.startswith("qtd_evento_cat_")
    ]

    for col in event_count_cols:
        new_col = col.replace("qtd_evento_cat_", "perc_evento_cat_")
        df[new_col] = safe_divide(df[col], df["qtd_eventos"])

    perc_cols = [c for c in df.columns if c.startswith("perc_evento_cat_")]
    df[perc_cols] = df[perc_cols].fillna(0)

    return df


def add_event_intensity_features(df):
    """
    Cria features de intensidade de eventos:
    - log quantidade de eventos
    - flag sem eventos
    - faixa por quantil
    """
    df = df.copy()

    if "qtd_eventos" not in df.columns:
        print("[WARN] qtd_eventos não encontrada. Pulando intensidade de eventos.")
        return df

    df["qtd_eventos_log1p"] = np.log1p(df["qtd_eventos"].fillna(0))
    df["flag_sem_eventos"] = df["qtd_eventos"].isna().astype(int)

    try:
        df["qtd_eventos_faixa_q"] = pd.qcut(
            df["qtd_eventos"],
            q=5,
            duplicates="drop"
        ).astype(str)
    except Exception:
        df["qtd_eventos_faixa_q"] = "sem_faixa"

    return df


def add_event_complexity_features(df):
    """
    Cria score simples de complexidade processual baseado em:
    - volume de eventos
    - diversidade de categorias
    - duração da trajetória de eventos
    """
    df = df.copy()

    components = []

    if "qtd_eventos_log1p" not in df.columns and "qtd_eventos" in df.columns:
        df["qtd_eventos_log1p"] = np.log1p(df["qtd_eventos"].fillna(0))

    if "qtd_eventos_log1p" in df.columns:
        components.append("qtd_eventos_log1p")

    if "qtd_categorias_evento_distintas" in df.columns:
        df["qtd_categorias_evento_distintas_log1p"] = np.log1p(
            df["qtd_categorias_evento_distintas"].fillna(0)
        )
        components.append("qtd_categorias_evento_distintas_log1p")

    if "dias_entre_primeiro_ultimo_evento" in df.columns:
        df["dias_entre_primeiro_ultimo_evento_log1p"] = np.log1p(
            df["dias_entre_primeiro_ultimo_evento"].clip(lower=0).fillna(0)
        )
        components.append("dias_entre_primeiro_ultimo_evento_log1p")

    if components:
        df["score_complexidade_processual_simples"] = (
            df[components]
            .rank(pct=True)
            .mean(axis=1)
        )

    return df


def build_recent_event_features(
    df_eventos,
    process_id_col="numero_processo",
    date_col="data",
    category_col="tipo_categoria",
    windows=None,
    data_ref=None
):
    """
    Cria features de quantidade de eventos nas últimas janelas de tempo.
    """
    if windows is None:
        windows = [30, 60, 90, 180, 365]

    df = df_eventos.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    if data_ref is None:
        data_ref = df[date_col].max()

    features = pd.DataFrame({
        process_id_col: df[process_id_col].dropna().unique()
    })

    for window in windows:
        cutoff = data_ref - pd.Timedelta(days=window)
        temp = df[df[date_col] >= cutoff].copy()

        count_features = (
            temp
            .groupby(process_id_col)
            .size()
            .reset_index(name=f"qtd_eventos_ultimos_{window}_dias")
        )

        features = features.merge(count_features, on=process_id_col, how="left")

        if category_col in temp.columns:
            cat_features = (
                pd.crosstab(temp[process_id_col], temp[category_col])
                .add_prefix(f"qtd_evento_cat_ultimos_{window}_dias_")
                .reset_index()
            )
            features = features.merge(cat_features, on=process_id_col, how="left")

    cols = [c for c in features.columns if c != process_id_col]
    features[cols] = features[cols].fillna(0)

    return features


def build_last_n_event_sequences(
    df_eventos,
    process_id_col="numero_processo",
    date_col="data",
    category_col="tipo_categoria",
    n_values=None
):
    """
    Cria sequências textuais dos últimos N eventos por processo.
    """
    if n_values is None:
        n_values = [3, 5, 10]

    df = df_eventos.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.sort_values([process_id_col, date_col])

    features = pd.DataFrame({
        process_id_col: df[process_id_col].dropna().unique()
    })

    for n in n_values:
        seq = (
            df
            .groupby(process_id_col)[category_col]
            .apply(lambda x: " > ".join(x.dropna().astype(str).tail(n)))
            .reset_index(name=f"ultimos_{n}_eventos")
        )
        features = features.merge(seq, on=process_id_col, how="left")

    return features


def build_transition_features(
    df_eventos,
    process_id_col="numero_processo",
    date_col="data",
    category_col="tipo_categoria",
    top_n=50
):
    """
    Cria features de transições entre categorias consecutivas de eventos.
    """
    df = df_eventos.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.sort_values([process_id_col, date_col])

    df["proxima_categoria_evento"] = (
        df
        .groupby(process_id_col)[category_col]
        .shift(-1)
    )

    df_trans = df.dropna(subset=["proxima_categoria_evento"]).copy()

    df_trans["transicao_evento"] = (
        df_trans[category_col].astype(str) +
        "_para_" +
        df_trans["proxima_categoria_evento"].astype(str)
    )

    transition_freq = (
        df_trans["transicao_evento"]
        .value_counts()
        .reset_index()
    )
    transition_freq.columns = ["transicao_evento", "qtd"]
    transition_freq["perc"] = transition_freq["qtd"] / len(df_trans)

    top_transitions = transition_freq.head(top_n)["transicao_evento"].tolist()
    df_top = df_trans[df_trans["transicao_evento"].isin(top_transitions)].copy()

    transition_features = (
        pd.crosstab(df_top[process_id_col], df_top["transicao_evento"])
        .add_prefix("qtd_transicao_")
        .reset_index()
    )

    transition_features.columns = [
        re.sub(r"[^a-zA-Z0-9_]", "_", c)
        for c in transition_features.columns
    ]

    return transition_features, transition_freq
'''

files["src/feature_engineering/entity_features.py"] = '''"""
Features de entidades: advogados, requerentes e requeridos.
"""

import ast
import pandas as pd
from .utils import normalize_text


def parse_list_like(value):
    """
    Tenta transformar uma célula em lista de entidades normalizadas.

    Aceita:
    - lista Python real
    - string no formato de lista
    - string separada por ; | ,
    - string simples
    """
    if pd.isna(value):
        return []

    if isinstance(value, list):
        return [normalize_text(x) for x in value if normalize_text(x)]

    text = str(value).strip()

    try:
        parsed = ast.literal_eval(text)
        if isinstance(parsed, list):
            return [normalize_text(x) for x in parsed if normalize_text(x)]
    except Exception:
        pass

    for sep in [";", "|", ","]:
        if sep in text:
            return [normalize_text(x) for x in text.split(sep) if normalize_text(x)]

    norm = normalize_text(text)
    return [norm] if norm else []


def add_list_entity_features(df, list_cols=None):
    """
    Cria features de quantidade e primeira entidade para colunas tipo lista.

    Exemplo:
    - qtd_adv_requerente_lista
    - primeiro_adv_requerente_lista
    """
    df = df.copy()

    if list_cols is None:
        list_cols = [
            "adv_requerente_lista",
            "adv_requerido_lista",
            "requerente_lista",
            "requerido_lista",
        ]

    list_cols = [c for c in list_cols if c in df.columns]

    for col in list_cols:
        parsed_col = f"{col}_parsed"
        count_col = f"qtd_{col}"
        first_col = f"primeiro_{col}"

        df[parsed_col] = df[col].apply(parse_list_like)
        df[count_col] = df[parsed_col].apply(len)
        df[first_col] = df[parsed_col].apply(
            lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None
        )

    return df
'''

files["src/feature_engineering/target_encoding.py"] = '''"""
Target encoding suavizado para variáveis jurídicas de alta cardinalidade.

Atenção:
Este módulo cria target encoding exploratório.
Para um modelo oficial, use encoding out-of-fold ou point-in-time.
"""

import re
import pandas as pd


def smooth_target_rate(df, group_col, target_col="perda_banco", k=30, min_count=1):
    """
    Calcula taxa suavizada:
    (perdas_grupo + media_global * k) / (total_grupo + k)
    """
    if group_col not in df.columns:
        raise KeyError(f"Coluna não encontrada: {group_col}")

    if target_col not in df.columns:
        raise KeyError(f"Target não encontrado: {target_col}")

    tmp = df[[group_col, target_col]].copy()
    tmp = tmp.dropna(subset=[target_col])

    global_rate = tmp[target_col].mean()

    agg = (
        tmp
        .groupby(group_col, dropna=False)[target_col]
        .agg(["sum", "count", "mean"])
        .reset_index()
        .rename(columns={
            "sum": "qtd_perdas",
            "count": "qtd_processos",
            "mean": "taxa_perda_bruta"
        })
    )

    agg = agg[agg["qtd_processos"] >= min_count].copy()

    output_col = f"taxa_perda_suavizada_{group_col}"

    agg[output_col] = (
        (agg["qtd_perdas"] + global_rate * k) /
        (agg["qtd_processos"] + k)
    )

    return agg


def add_smooth_target_rate_features(
    df,
    group_cols,
    target_col="perda_banco",
    k=30,
    min_count=1,
    reports_dir=None
):
    """
    Adiciona features de taxa suavizada para uma lista de colunas.
    Retorna:
    - df com novas features
    - dicionário de relatórios por coluna
    """
    df = df.copy()
    reports = {}

    group_cols = [c for c in group_cols if c in df.columns]

    for col in group_cols:
        print(f"[INFO] Calculando taxa suavizada para: {col}")

        rate_df = smooth_target_rate(
            df,
            group_col=col,
            target_col=target_col,
            k=k,
            min_count=min_count
        )

        output_col = f"taxa_perda_suavizada_{col}"
        hist_col = f"qtd_hist_{col}"

        reports[col] = rate_df.copy()

        df = df.merge(
            rate_df[[col, output_col, "qtd_processos"]],
            on=col,
            how="left"
        )

        df = df.rename(columns={"qtd_processos": hist_col})

        if reports_dir is not None:
            safe_name = re.sub(r"[^a-zA-Z0-9_]", "_", col)
            rate_df.to_csv(reports_dir / f"target_encoding_{safe_name}.csv", index=False)

    return df, reports
'''

files["src/feature_engineering/leakage.py"] = '''"""
Identificação e remoção de colunas com risco de leakage.
"""


def identify_leakage_columns(columns):
    """
    Identifica colunas perigosas para modelagem preditiva inicial.

    Atenção:
    Esta lista é conservadora. Revise com o jurídico e com o objetivo do modelo.
    """
    leakage_patterns = [
        "resultado",
        "sentenca_tipo",
        "texto_sentenca",
        "texto_tutela",
        "acordao",
        "condenacao",
        "transito",
        "valor_arbitrado",
        "valor_do_acordo",
        "honorario",
        "alvara",
        "procedente_prob",
        "procedente_parc_procedente_prob",
        "dano_moral_prob",
        "condenacao_valor_prob",
        "acordo_prob",
        "provavel",
        "_prob",
        "_v2",
        "list_v2",
        "link_",
        "link",
    ]

    leakage_cols = []

    for col in columns:
        c = col.lower()
        if any(p in c for p in leakage_patterns):
            leakage_cols.append(col)

    return sorted(set(leakage_cols))


def remove_leakage_columns(df, target_col="perda_banco", keep_cols=None):
    """
    Remove colunas com risco de leakage, preservando target e colunas explicitamente mantidas.
    """
    df = df.copy()

    if keep_cols is None:
        keep_cols = []

    keep = set([target_col] + keep_cols)

    leakage_cols = identify_leakage_columns(df.columns)

    cols_to_drop = [
        c for c in leakage_cols
        if c in df.columns and c not in keep
    ]

    df = df.drop(columns=cols_to_drop, errors="ignore")

    return df, cols_to_drop
'''

files["src/feature_engineering/feature_selection.py"] = '''"""
Relatórios simples para priorizar features candidatas antes do modelo.
"""

import pandas as pd
import numpy as np


def split_feature_types(df, id_cols=None, target_cols=None):
    """
    Separa features numéricas e categóricas.
    """
    if id_cols is None:
        id_cols = ["numero_processo"]

    if target_cols is None:
        target_cols = ["perda_banco", "target_source"]

    exclude = set([c for c in id_cols + target_cols if c in df.columns])

    feature_cols = [c for c in df.columns if c not in exclude]

    numeric_features = [
        c for c in feature_cols
        if pd.api.types.is_numeric_dtype(df[c])
    ]

    categorical_features = [
        c for c in feature_cols
        if not pd.api.types.is_numeric_dtype(df[c])
    ]

    return feature_cols, numeric_features, categorical_features


def categorical_cardinality_report(df, categorical_features):
    """
    Calcula cardinalidade das features categóricas.
    """
    rows = []

    for col in categorical_features:
        nunique = df[col].nunique(dropna=True)
        rows.append({
            "coluna": col,
            "qtd_distintos": int(nunique),
            "perc_distintos": nunique / len(df) if len(df) else np.nan
        })

    return pd.DataFrame(rows).sort_values("qtd_distintos", ascending=False)


def numeric_feature_strength(df, numeric_features, target_col="perda_banco"):
    """
    Mede associação simples de features numéricas com o target.
    """
    df_train = df[df[target_col].notna()].copy()
    df_train[target_col] = df_train[target_col].astype(int)

    rows = []

    for col in numeric_features:
        if col == target_col:
            continue

        s = pd.to_numeric(df_train[col], errors="coerce")

        if s.notna().sum() < 30:
            continue

        try:
            corr = s.corr(df_train[target_col])
        except Exception:
            corr = np.nan

        rows.append({
            "feature": col,
            "non_null": int(s.notna().sum()),
            "perc_non_null": float(s.notna().mean()),
            "mean_target_0": s[df_train[target_col] == 0].mean(),
            "mean_target_1": s[df_train[target_col] == 1].mean(),
            "diff_mean_1_minus_0": (
                s[df_train[target_col] == 1].mean() -
                s[df_train[target_col] == 0].mean()
            ),
            "corr_with_target": corr,
            "abs_corr_with_target": abs(corr) if pd.notna(corr) else np.nan
        })

    return pd.DataFrame(rows).sort_values("abs_corr_with_target", ascending=False)


def categorical_feature_strength(df, categorical_features, target_col="perda_banco", min_count=30):
    """
    Mede variação de taxa de perda nas categorias de cada feature categórica.
    """
    df_train = df[df[target_col].notna()].copy()
    df_train[target_col] = df_train[target_col].astype(int)

    rows = []
    global_rate = df_train[target_col].mean()

    for col in categorical_features:
        temp = (
            df_train
            .groupby(col, dropna=False)
            .agg(
                qtd=(target_col, "count"),
                taxa_perda=(target_col, "mean")
            )
            .reset_index()
        )

        temp = temp[temp["qtd"] >= min_count].copy()

        if temp.empty:
            continue

        temp["abs_diff_vs_global"] = (temp["taxa_perda"] - global_rate).abs()

        rows.append({
            "feature": col,
            "qtd_categorias_validas": len(temp),
            "max_taxa_perda": temp["taxa_perda"].max(),
            "min_taxa_perda": temp["taxa_perda"].min(),
            "range_taxa_perda": temp["taxa_perda"].max() - temp["taxa_perda"].min(),
            "max_abs_diff_vs_global": temp["abs_diff_vs_global"].max()
        })

    return pd.DataFrame(rows).sort_values("max_abs_diff_vs_global", ascending=False)


def build_feature_candidate_report(
    df,
    id_cols=None,
    target_cols=None,
    target_col="perda_banco",
    max_cat_cardinality=100,
    min_count=30,
    reports_dir=None
):
    """
    Gera relatórios de força de features e retorna lista de candidatas.
    """
    feature_cols, numeric_features, categorical_features = split_feature_types(
        df,
        id_cols=id_cols,
        target_cols=target_cols
    )

    cat_card = categorical_cardinality_report(df, categorical_features)

    safe_categorical_features = (
        cat_card
        .query("qtd_distintos <= @max_cat_cardinality")
        ["coluna"]
        .tolist()
    )

    num_strength = numeric_feature_strength(
        df,
        numeric_features,
        target_col=target_col
    )

    cat_strength = categorical_feature_strength(
        df,
        safe_categorical_features,
        target_col=target_col,
        min_count=min_count
    )

    top_numeric = num_strength.head(100)["feature"].tolist() if not num_strength.empty else []
    top_categorical = cat_strength.head(50)["feature"].tolist() if not cat_strength.empty else []

    candidate_features = list(dict.fromkeys(top_numeric + top_categorical))

    feature_ranking = pd.DataFrame({
        "feature": candidate_features,
        "tipo": [
            "numeric" if f in numeric_features else "categorical"
            for f in candidate_features
        ]
    })

    if reports_dir is not None:
        cat_card.to_csv(reports_dir / "categorical_feature_cardinality_model_abt.csv", index=False)
        num_strength.to_csv(reports_dir / "numeric_feature_strength.csv", index=False)
        cat_strength.to_csv(reports_dir / "categorical_feature_strength.csv", index=False)
        feature_ranking.to_csv(reports_dir / "candidate_features_for_model.csv", index=False)

    return {
        "feature_cols": feature_cols,
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
        "safe_categorical_features": safe_categorical_features,
        "candidate_features": candidate_features,
        "cat_cardinality": cat_card,
        "numeric_strength": num_strength,
        "categorical_strength": cat_strength,
        "feature_ranking": feature_ranking,
    }
'''

files["notebook_feature_engineering_example.py"] = '''"""
Exemplo de uso dos módulos em um notebook.

Este arquivo não precisa ser executado como script.
Use como referência para copiar célula por célula no notebook do Safra.
"""

# %% 1. Imports e configs

import pandas as pd

from src.feature_engineering.config import (
    PROCESS_ID_COL,
    TARGET_COL,
    PROCESSED_DIR,
    INTERIM_DIR,
    REPORTS_DIR,
    MAIN_VALUE_COL,
    MAIN_DATE_COLS,
    LIST_ENTITY_COLS,
    GROUP_COLS_FOR_ENCODING,
    RECENT_WINDOWS,
)

from src.feature_engineering.value_features import (
    profile_value_columns,
    add_value_features,
)

from src.feature_engineering.date_features import (
    add_main_date_features,
)

from src.feature_engineering.event_features import (
    add_event_ratio_features,
    add_event_intensity_features,
    add_event_complexity_features,
    build_recent_event_features,
    build_last_n_event_sequences,
    build_transition_features,
)

from src.feature_engineering.entity_features import (
    add_list_entity_features,
)

from src.feature_engineering.target_encoding import (
    add_smooth_target_rate_features,
)

from src.feature_engineering.leakage import (
    remove_leakage_columns,
)

from src.feature_engineering.feature_selection import (
    build_feature_candidate_report,
)


# %% 2. Carregar ABT inicial da EDA

df_abt = pd.read_parquet(PROCESSED_DIR / "abt_eda_inicial.parquet")
print(df_abt.shape)
df_abt.head()


# %% 3. Features de valor

value_report = profile_value_columns(
    df_abt,
    output_path=REPORTS_DIR / "value_columns_profile.csv"
)

df_abt = add_value_features(df_abt, value_col=MAIN_VALUE_COL)


# %% 4. Features de data

df_abt, data_ref = add_main_date_features(
    df_abt,
    main_date_cols=MAIN_DATE_COLS,
    data_ref=None
)

print("Data de referência:", data_ref)


# %% 5. Features da ABT de eventos já criada na EDA

df_abt = add_event_ratio_features(df_abt)
df_abt = add_event_intensity_features(df_abt)
df_abt = add_event_complexity_features(df_abt)


# %% 6. Features de entidades/listas

df_abt = add_list_entity_features(df_abt, list_cols=LIST_ENTITY_COLS)


# %% 7. Opcional: features adicionais a partir da base de eventos tratada

# Se você tiver gerado eventos_tratados_eda.parquet pela EDA:
eventos_path = PROCESSED_DIR / "eventos_tratados_eda.parquet"

if eventos_path.exists():
    df_eventos = pd.read_parquet(eventos_path)
    print(df_eventos.shape)

    recent_event_features = build_recent_event_features(
        df_eventos,
        process_id_col=PROCESS_ID_COL,
        date_col="data",
        category_col="tipo_categoria",
        windows=RECENT_WINDOWS,
        data_ref=data_ref,
    )

    df_abt = df_abt.merge(
        recent_event_features,
        on=PROCESS_ID_COL,
        how="left"
    )

    recent_cols = [c for c in recent_event_features.columns if c != PROCESS_ID_COL]
    df_abt[recent_cols] = df_abt[recent_cols].fillna(0)

    sequence_features = build_last_n_event_sequences(
        df_eventos,
        process_id_col=PROCESS_ID_COL,
        date_col="data",
        category_col="tipo_categoria",
        n_values=[3, 5, 10],
    )

    df_abt = df_abt.merge(
        sequence_features,
        on=PROCESS_ID_COL,
        how="left"
    )

    transition_features, transition_freq = build_transition_features(
        df_eventos,
        process_id_col=PROCESS_ID_COL,
        date_col="data",
        category_col="tipo_categoria",
        top_n=50,
    )

    transition_freq.to_csv(REPORTS_DIR / "transition_frequency_report.csv", index=False)

    df_abt = df_abt.merge(
        transition_features,
        on=PROCESS_ID_COL,
        how="left"
    )

    transition_cols = [c for c in transition_features.columns if c != PROCESS_ID_COL]
    df_abt[transition_cols] = df_abt[transition_cols].fillna(0)

else:
    print("Arquivo de eventos tratados não encontrado. Pulando features adicionais de eventos.")


# %% 8. Target encoding suavizado exploratório

encoding_cols = [c for c in GROUP_COLS_FOR_ENCODING if c in df_abt.columns]

df_abt, encoding_reports = add_smooth_target_rate_features(
    df_abt,
    group_cols=encoding_cols,
    target_col=TARGET_COL,
    k=30,
    min_count=1,
    reports_dir=REPORTS_DIR,
)


# %% 9. Remover colunas de leakage para ABT modelável

df_model_abt, removed_leakage_cols = remove_leakage_columns(
    df_abt,
    target_col=TARGET_COL,
    keep_cols=[PROCESS_ID_COL, "target_source"],
)

pd.DataFrame({"coluna": removed_leakage_cols}).to_csv(
    REPORTS_DIR / "leakage_columns_to_remove_features_step.csv",
    index=False,
)

print("ABT completa:", df_abt.shape)
print("ABT modelável:", df_model_abt.shape)


# %% 10. Relatórios de features candidatas

feature_reports = build_feature_candidate_report(
    df_model_abt,
    id_cols=[PROCESS_ID_COL],
    target_cols=[TARGET_COL, "target_source"],
    target_col=TARGET_COL,
    max_cat_cardinality=100,
    min_count=30,
    reports_dir=REPORTS_DIR,
)

candidate_features = feature_reports["candidate_features"]
print("Qtd features candidatas:", len(candidate_features))


# %% 11. Salvar saídas

df_abt.to_parquet(
    PROCESSED_DIR / "abt_feature_engineering_juridico.parquet",
    index=False,
)

df_model_abt.to_parquet(
    PROCESSED_DIR / "abt_model_abt_sem_leakage.parquet",
    index=False,
)

final_cols = [PROCESS_ID_COL, TARGET_COL, "target_source"] + candidate_features
final_cols = [c for c in final_cols if c in df_model_abt.columns]

df_model_ready = df_model_abt[final_cols].copy()

df_model_ready.to_parquet(
    PROCESSED_DIR / "abt_model_ready_juridico.parquet",
    index=False,
)

print("Arquivo final salvo:", PROCESSED_DIR / "abt_model_ready_juridico.parquet")
print(df_model_ready.shape)
'''

files["README.md"] = """
# Feature Engineering Jurídico — Módulos para Notebook

Este pacote contém módulos pequenos para testar feature engineering jurídico em notebook, a partir da ABT inicial gerada pela EDA forense.

## Pré-requisito

Rode antes o script:

```bash
python eda_forense_juridico.py
"""