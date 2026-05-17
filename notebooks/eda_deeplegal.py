from pathlib import Path

script = r'''"""
EDA Forense para Bases Jurídicas de Processos e Eventos
======================================================

Objetivo
--------
Conduzir uma análise exploratória forense sobre duas bases:

1. Base de processos:
   - Uma linha por processo/protesto.
   - Contém dados estruturados do processo, partes, assunto, valores,
     andamento, resultado, sinais e predições externas.

2. Base de eventos:
   - Várias linhas por processo.
   - Contém a sequência de eventos/movimentos processuais:
     numero, tipo, texto, data.

Esta EDA foi desenhada para:
- Validar o grão das bases.
- Avaliar qualidade de chaves.
- Investigar nulos, cardinalidade e valores dominantes.
- Separar colunas candidatas a feature, target, leakage e descarte.
- Normalizar e categorizar eventos processuais.
- Criar uma primeira ABT exploratória com uma linha por processo.
- Gerar relatórios CSV para auditoria e interpretação.

Importante
----------
Este script NÃO treina modelo e NÃO cria features avançadas para modelagem.
Ele prepara a análise exploratória e gera uma ABT inicial.

Como usar
---------
1. Crie uma estrutura simples de pastas:

   data/
     raw/
     processed/
   outputs/
     reports/

2. Coloque os arquivos brutos em data/raw:
   - processos.parquet ou processos.csv
   - eventos.parquet ou eventos.csv

3. Ajuste as variáveis PROCESSOS_FILE e EVENTOS_FILE no bloco CONFIGURAÇÕES.

4. Execute:

   python eda_forense_juridico.py

Requisitos
----------
pandas
numpy
pyarrow  # para parquet
openpyxl # somente se for ler Excel

"""

import os
import re
import unicodedata
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd


# =============================================================================
# 0. CONFIGURAÇÕES
# =============================================================================

pd.set_option("display.max_columns", 200)
pd.set_option("display.max_rows", 200)
pd.set_option("display.width", 200)

# Colunas principais
PROCESS_ID_COL = "numero_processo"

EVENT_NUM_COL = "numero"
EVENT_TYPE_COL = "tipo"
EVENT_TEXT_COL = "texto"
EVENT_DATE_COL = "data"

TARGET_COL = "perda_banco"

# Thresholds de EDA
NULL_THRESHOLD = 0.80
LOW_VARIANCE_THRESHOLD = 0.98

# Diretórios
BASE_DIR = Path(".")
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
REPORTS_DIR = BASE_DIR / "outputs" / "reports"

for path in [RAW_DIR, PROCESSED_DIR, REPORTS_DIR]:
    path.mkdir(parents=True, exist_ok=True)

# Arquivos de entrada
# Ajuste aqui se seus arquivos tiverem outros nomes.
PROCESSOS_FILE = RAW_DIR / "processos.parquet"
EVENTOS_FILE = RAW_DIR / "eventos.parquet"

# Caso estejam em CSV, altere para:
# PROCESSOS_FILE = RAW_DIR / "processos.csv"
# EVENTOS_FILE = RAW_DIR / "eventos.csv"


# =============================================================================
# 1. FUNÇÕES UTILITÁRIAS
# =============================================================================

NULL_STRINGS = {"", "null", "nan", "none", "na", "n/a", "-"}


def read_data(path, columns=None, nrows=None):
    """
    Lê dados em Parquet, CSV ou Excel.

    Parameters
    ----------
    path : str or Path
        Caminho do arquivo.
    columns : list[str], optional
        Colunas a serem lidas.
    nrows : int, optional
        Número de linhas para leitura parcial. Aplicável principalmente a CSV.

    Returns
    -------
    pd.DataFrame
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    suffix = path.suffix.lower()

    if suffix == ".parquet":
        return pd.read_parquet(path, columns=columns)

    if suffix == ".csv":
        return pd.read_csv(path, usecols=columns, nrows=nrows)

    if suffix in [".xlsx", ".xls"]:
        return pd.read_excel(path, usecols=columns, nrows=nrows)

    raise ValueError(f"Formato não suportado: {path}")


def save_report(df, filename):
    """
    Salva um DataFrame como CSV em outputs/reports.
    """
    output_path = REPORTS_DIR / filename
    df.to_csv(output_path, index=False)
    print(f"Relatório salvo em: {output_path}")


def normalize_text(text):
    """
    Normaliza textos:
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
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    if text in NULL_STRINGS:
        return None

    return text


def is_null_like_series(s):
    """
    Considera nulos reais e strings que representam nulo.
    """
    if s.dtype == "object" or str(s.dtype) == "category":
        return s.isna() | s.astype(str).str.strip().str.lower().isin(NULL_STRINGS)
    return s.isna()


def safe_display_head(df, n=10, title=None):
    """
    Exibe uma amostra no terminal sem quebrar o script em ambientes simples.
    """
    if title:
        print("\n" + "=" * 100)
        print(title)
        print("=" * 100)
    print(df.head(n).to_string(index=False))


# =============================================================================
# 2. FUNÇÕES DE AUDITORIA E EDA
# =============================================================================

def basic_overview(df, name):
    """
    Gera visão geral da base.
    """
    overview = {
        "base": name,
        "linhas": len(df),
        "colunas": df.shape[1],
        "memoria_mb": round(df.memory_usage(deep=True).sum() / 1024**2, 2),
        "duplicatas_completas": int(df.duplicated().sum())
    }

    print("\n" + "=" * 100)
    print(f"OVERVIEW — {name}")
    print("=" * 100)
    for k, v in overview.items():
        print(f"{k}: {v}")

    print("\nTipos de dados:")
    print(df.dtypes.value_counts())

    return pd.DataFrame([overview])


def key_audit(df, key_col, name):
    """
    Audita a chave principal da base.
    """
    print("\n" + "=" * 100)
    print(f"AUDITORIA DE CHAVE — {name}")
    print("=" * 100)

    if key_col not in df.columns:
        raise KeyError(f"Coluna de chave não encontrada em {name}: {key_col}")

    total_rows = len(df)
    unique_keys = df[key_col].nunique(dropna=True)
    null_keys = df[key_col].isna().sum()
    duplicated_rows_beyond_unique = total_rows - unique_keys

    print(f"Total de linhas: {total_rows:,}")
    print(f"Chaves únicas: {unique_keys:,}")
    print(f"Chaves nulas: {null_keys:,}")
    print(f"Linhas além das chaves únicas: {duplicated_rows_beyond_unique:,}")

    duplicated = (
        df.groupby(key_col, dropna=False)
        .size()
        .reset_index(name="qtd_linhas")
        .query("qtd_linhas > 1")
        .sort_values("qtd_linhas", ascending=False)
    )

    print(f"Quantidade de chaves duplicadas: {len(duplicated):,}")

    return duplicated


def process_event_relationship_audit(df_processos, df_eventos, process_id_col):
    """
    Audita relação entre base de processos e base de eventos.
    """
    processos_set = set(df_processos[process_id_col].dropna().astype(str))
    eventos_set = set(df_eventos[process_id_col].dropna().astype(str))

    processos_com_eventos = processos_set.intersection(eventos_set)
    processos_sem_eventos = processos_set - eventos_set
    eventos_sem_processo = eventos_set - processos_set

    result = {
        "qtd_processos": len(processos_set),
        "qtd_processos_na_base_eventos": len(eventos_set),
        "processos_com_eventos": len(processos_com_eventos),
        "processos_sem_eventos": len(processos_sem_eventos),
        "ids_eventos_sem_processo": len(eventos_sem_processo),
        "perc_processos_com_eventos": len(processos_com_eventos) / len(processos_set) if processos_set else np.nan,
        "perc_processos_sem_eventos": len(processos_sem_eventos) / len(processos_set) if processos_set else np.nan
    }

    print("\n" + "=" * 100)
    print("AUDITORIA PROCESSOS × EVENTOS")
    print("=" * 100)
    for k, v in result.items():
        print(f"{k}: {v}")

    return pd.DataFrame([result]), processos_sem_eventos, eventos_sem_processo


def null_report(df):
    """
    Relatório de nulos por coluna.
    Considera também strings vazias, 'null', 'nan', 'none', 'na', 'n/a' e '-'.
    """
    rows = []
    n = len(df)

    for col in df.columns:
        null_mask = is_null_like_series(df[col])
        qtd_null = int(null_mask.sum())
        perc_null = qtd_null / n if n > 0 else np.nan

        rows.append({
            "coluna": col,
            "dtype": str(df[col].dtype),
            "qtd_nulos": qtd_null,
            "perc_nulos": perc_null,
            "qtd_nao_nulos": n - qtd_null
        })

    report = pd.DataFrame(rows).sort_values("perc_nulos", ascending=False)
    return report


def classify_null_severity(perc):
    """
    Classifica percentual de nulos.
    """
    if perc >= 0.95:
        return "critico_95_mais"
    if perc >= 0.80:
        return "alto_80_95"
    if perc >= 0.50:
        return "medio_50_80"
    if perc >= 0.20:
        return "baixo_20_50"
    return "baixo_menos_20"


def cardinality_report(df):
    """
    Relatório de cardinalidade por coluna.
    """
    rows = []
    n = len(df)

    for col in df.columns:
        nunique = df[col].nunique(dropna=True)
        perc_unique = nunique / n if n > 0 else np.nan

        rows.append({
            "coluna": col,
            "dtype": str(df[col].dtype),
            "qtd_distintos": int(nunique),
            "perc_distintos": perc_unique
        })

    return pd.DataFrame(rows).sort_values("qtd_distintos", ascending=False)


def dominant_value_report(df):
    """
    Relatório do valor dominante por coluna.
    """
    rows = []
    n = len(df)

    for col in df.columns:
        vc = df[col].value_counts(dropna=False)

        if len(vc) == 0:
            continue

        top_value = vc.index[0]
        top_count = int(vc.iloc[0])
        top_perc = top_count / n if n > 0 else np.nan

        rows.append({
            "coluna": col,
            "dtype": str(df[col].dtype),
            "valor_mais_frequente": top_value,
            "qtd_valor_mais_frequente": top_count,
            "perc_valor_mais_frequente": top_perc
        })

    return pd.DataFrame(rows).sort_values("perc_valor_mais_frequente", ascending=False)


def numeric_summary(df):
    """
    Resumo estatístico de colunas numéricas.
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    rows = []

    for col in numeric_cols:
        s = pd.to_numeric(df[col], errors="coerce")
        rows.append({
            "coluna": col,
            "count": int(s.notna().sum()),
            "mean": s.mean(),
            "std": s.std(),
            "min": s.min(),
            "p01": s.quantile(0.01),
            "p05": s.quantile(0.05),
            "p25": s.quantile(0.25),
            "p50": s.quantile(0.50),
            "p75": s.quantile(0.75),
            "p95": s.quantile(0.95),
            "p99": s.quantile(0.99),
            "max": s.max()
        })

    return pd.DataFrame(rows)


def date_report(df):
    """
    Investiga colunas que parecem datas pelo nome.
    """
    date_like_cols = [
        c for c in df.columns
        if "data" in c.lower() or c.lower() in ["modified"]
    ]

    rows = []

    for col in date_like_cols:
        s = pd.to_datetime(df[col], errors="coerce")

        rows.append({
            "coluna": col,
            "dtype_original": str(df[col].dtype),
            "qtd_nao_nulos_convertidos": int(s.notna().sum()),
            "perc_nao_nulos_convertidos": s.notna().mean(),
            "min_data": s.min(),
            "max_data": s.max(),
            "qtd_nulos_apos_conversao": int(s.isna().sum()),
            "perc_nulos_apos_conversao": s.isna().mean()
        })

    return pd.DataFrame(rows).sort_values("perc_nao_nulos_convertidos", ascending=False)


def classify_column_by_name(col):
    """
    Classifica colunas de processos por padrão de nome.
    """
    c = col.lower()

    if "prob" in c or "provavel" in c or "predicao" in c:
        return "predicao_externa"

    if "_v2" in c or "deprec" in c or "list_v2" in c:
        return "deprecated"

    if "link" in c:
        return "link"

    if "resultado" in c or "sentenca" in c or "acordao" in c or "condenacao" in c or "transito" in c:
        return "resultado_ou_pos_decisao"

    if "data" in c or c.endswith("_data") or "modified" in c:
        return "data"

    if "valor" in c or "vl" in c or "honorario" in c or "multa" in c:
        return "valor"

    if "adv" in c or "escritorio" in c or "requerente" in c or "requerido" in c:
        return "partes_advogados"

    if "juiz" in c or "julgador" in c or "vara" in c or "orgao" in c:
        return "julgador_orgao"

    if "assunto" in c or "classe" in c or "area" in c or "tipo_de_processo" in c:
        return "classe_assunto"

    if "movimento" in c or "fase" in c or "status" in c:
        return "andamento"

    if c.endswith("_conf") or c.endswith("_cont") or c.endswith("_duracao"):
        return "sinal_derivado"

    return "outros"


def identify_external_prediction_cols(columns):
    """
    Identifica colunas que parecem ser predições externas.
    """
    cols = []
    for col in columns:
        c = col.lower()
        if "prob" in c or "provavel" in c or "predicao" in c:
            cols.append(col)
    return cols


def identify_deprecated_cols(columns):
    """
    Identifica colunas deprecated/v2.
    """
    cols = []
    for col in columns:
        c = col.lower()
        if "_v2" in c or "list_v2" in c or "deprec" in c:
            cols.append(col)
    return cols


def identify_link_cols(columns):
    """
    Identifica colunas de link.
    """
    return [col for col in columns if "link" in col.lower()]


def identify_long_text_cols(columns):
    """
    Identifica textos longos inicialmente não usados como feature.
    """
    patterns = [
        "texto_sentenca",
        "texto_tutela",
        "resultado_original",
        "valores_processo"
    ]
    return [col for col in columns if any(p in col.lower() for p in patterns)]


def identify_result_or_post_decision_cols(columns):
    """
    Identifica colunas ligadas a resultado ou eventos pós-decisão.
    """
    patterns = [
        "resultado",
        "sentenca",
        "acordao",
        "condenacao",
        "transito",
        "arquivado",
        "acordo",
        "alvara",
        "execucao",
        "valor_arbitrado"
    ]

    return [
        col for col in columns
        if any(p in col.lower() for p in patterns)
    ]


def recommend_column_usage(row, external_pred_cols, deprecated_cols, link_cols, long_text_cols, post_decision_cols):
    """
    Recomenda uso de coluna com base no perfil forense.
    """
    col = row["coluna"]
    group = row["grupo_inferido"]
    null_pct = row["perc_nulos"]
    cardinality_pct = row["perc_distintos"]

    if col in external_pred_cols:
        return "remover_feature__predicao_externa"

    if col in deprecated_cols:
        return "remover_feature__deprecated"

    if col in link_cols:
        return "remover_feature__link"

    if col in long_text_cols:
        return "remover_feature__texto_longo_inicialmente"

    if col in post_decision_cols:
        return "usar_como_target_ou_remover_por_leakage"

    if null_pct >= 0.95:
        return "remover_ou_analisar_flag_rara"

    if cardinality_pct > 0.80:
        return "alta_cardinalidade__avaliar_agregacao"

    if group in [
        "classe_assunto",
        "julgador_orgao",
        "partes_advogados",
        "valor",
        "data",
        "andamento",
        "sinal_derivado"
    ]:
        return "candidata_feature"

    return "avaliar"


# =============================================================================
# 3. FUNÇÕES PARA EVENTOS
# =============================================================================

def categorize_event_type(tipo_clean):
    """
    Classifica evento em macro categoria jurídica.
    A ordem das regras importa.
    """
    if pd.isna(tipo_clean) or tipo_clean == "":
        return "evento_desconhecido"

    t = tipo_clean

    # Acordo antes de decisão
    if any(x in t for x in ["homologacao de acordo", "acordo", "conciliacao positiva"]):
        return "acordo"

    if any(x in t for x in ["distribuicao", "distribuido", "protocolo inicial"]):
        return "distribuicao"

    if any(x in t for x in ["citacao", "citado", "mandado de citacao"]):
        return "citacao"

    if any(x in t for x in ["intimacao", "intimado", "publicacao", "diario"]):
        return "intimacao"

    if any(x in t for x in ["juntada", "peticao", "manifestacao"]):
        return "juntada_peticao"

    if any(x in t for x in ["contestacao", "defesa"]):
        return "contestacao"

    if any(x in t for x in ["audiencia", "conciliacao", "instrucao"]):
        return "audiencia"

    if "despacho" in t:
        return "despacho"

    if "sentenca" in t:
        return "sentenca"

    if any(x in t for x in ["embargos", "apelacao", "agravo", "recurso", "contrarrazoes"]):
        return "recurso"

    if any(x in t for x in ["acordao", "julgamento colegiado"]):
        return "acordao"

    if any(x in t for x in ["transito em julgado", "transitado"]):
        return "transito_julgado"

    if any(x in t for x in ["cumprimento de sentenca", "execucao", "penhora", "bloqueio", "bacenjud", "sisbajud", "renajud"]):
        return "execucao"

    if any(x in t for x in ["pagamento", "deposito", "alvara", "levantamento"]):
        return "pagamento"

    if any(x in t for x in ["arquivado", "arquivamento", "baixa definitiva"]):
        return "arquivamento"

    if any(x in t for x in ["decisao", "liminar", "tutela"]):
        return "decisao_interlocutoria"

    return "outros"


def sample_event_types_by_category(df, category_col="tipo_categoria", type_col="tipo_clean", n=20):
    """
    Gera exemplos dos tipos mais frequentes dentro de cada categoria.
    """
    samples = []

    for cat in sorted(df[category_col].dropna().unique()):
        unique_types = (
            df.loc[df[category_col] == cat, type_col]
            .dropna()
            .value_counts()
            .head(n)
            .reset_index()
        )
        unique_types.columns = [type_col, "qtd"]
        unique_types[category_col] = cat
        samples.append(unique_types)

    if not samples:
        return pd.DataFrame(columns=[type_col, "qtd", category_col])

    return pd.concat(samples, ignore_index=True)


def build_basic_event_features(df_eventos):
    """
    Cria features básicas por processo a partir dos eventos.
    """
    features = (
        df_eventos
        .groupby(PROCESS_ID_COL)
        .agg(
            qtd_eventos=(EVENT_TYPE_COL, "count"),
            qtd_tipos_evento_distintos=("tipo_clean", "nunique"),
            qtd_categorias_evento_distintas=("tipo_categoria", "nunique"),
            data_primeiro_evento=(EVENT_DATE_COL, "min"),
            data_ultimo_evento=(EVENT_DATE_COL, "max")
        )
        .reset_index()
    )

    features["dias_entre_primeiro_ultimo_evento"] = (
        features["data_ultimo_evento"] - features["data_primeiro_evento"]
    ).dt.days

    features["eventos_por_dia"] = (
        features["qtd_eventos"] /
        features["dias_entre_primeiro_ultimo_evento"].replace(0, np.nan)
    ).fillna(0)

    return features


def build_first_last_event_features(df_eventos):
    """
    Cria features de primeiro, último e penúltimo evento.
    """
    df = df_eventos.sort_values([PROCESS_ID_COL, EVENT_DATE_COL, EVENT_NUM_COL]).copy()

    primeiro_evento = (
        df
        .groupby(PROCESS_ID_COL)
        .first()
        .reset_index()[[PROCESS_ID_COL, EVENT_DATE_COL, "tipo_clean", "tipo_categoria"]]
        .rename(columns={
            EVENT_DATE_COL: "data_primeiro_evento_real",
            "tipo_clean": "primeiro_tipo_evento",
            "tipo_categoria": "primeira_categoria_evento"
        })
    )

    ultimo_evento = (
        df
        .groupby(PROCESS_ID_COL)
        .last()
        .reset_index()[[PROCESS_ID_COL, EVENT_DATE_COL, "tipo_clean", "tipo_categoria"]]
        .rename(columns={
            EVENT_DATE_COL: "data_ultimo_evento_real",
            "tipo_clean": "ultimo_tipo_evento",
            "tipo_categoria": "ultima_categoria_evento"
        })
    )

    df["ordem_reversa"] = df.groupby(PROCESS_ID_COL).cumcount(ascending=False)

    penultimo_evento = (
        df[df["ordem_reversa"] == 1]
        [[PROCESS_ID_COL, "tipo_clean", "tipo_categoria"]]
        .rename(columns={
            "tipo_clean": "penultimo_tipo_evento",
            "tipo_categoria": "penultima_categoria_evento"
        })
    )

    features = (
        primeiro_evento
        .merge(ultimo_evento, on=PROCESS_ID_COL, how="left")
        .merge(penultimo_evento, on=PROCESS_ID_COL, how="left")
    )

    return features


def build_event_category_features(df_eventos):
    """
    Cria contagens e flags por categoria de evento.
    """
    features = (
        pd.crosstab(
            df_eventos[PROCESS_ID_COL],
            df_eventos["tipo_categoria"]
        )
        .add_prefix("qtd_evento_cat_")
        .reset_index()
    )

    cat_count_cols = [c for c in features.columns if c.startswith("qtd_evento_cat_")]

    for col in cat_count_cols:
        cat_name = col.replace("qtd_evento_cat_", "")
        features[f"flag_teve_{cat_name}"] = (features[col] > 0).astype(int)

    return features


# =============================================================================
# 4. FUNÇÕES DE TARGET INICIAL
# =============================================================================

def classify_outcome_text(text):
    """
    Classifica texto de resultado em:
    0 = favorável ao banco / sem perda
    1 = perda / condenação / acordo / pagamento

    Atenção: 'improcedente' contém 'procedente'. Por isso, padrões favoráveis
    são avaliados antes de padrões desfavoráveis.
    """
    t = normalize_text(text)

    if t is None or t == "":
        return None

    favorable_patterns = [
        "improcedente",
        "improcedencia",
        "extinto",
        "extincao",
        "desistencia",
        "ausencia",
        "sem condenacao",
        "nao procedente"
    ]

    unfavorable_patterns = [
        "parcialmente procedente",
        "parc procedente",
        "procedente",
        "condenacao",
        "condenado",
        "acordo",
        "pagamento",
        "dano moral",
        "valor arbitrado"
    ]

    if any(p in t for p in favorable_patterns):
        return 0

    if any(p in t for p in unfavorable_patterns):
        return 1

    return None


def build_initial_target(df):
    """
    Cria target inicial perda_banco usando colunas candidatas de resultado.
    """
    target_candidate_cols = [
        "resultado_final_processo_text",
        "resultado_original_text",
        "resultadojulgamento_tipo",
        "sentenca_tipo",
        "resultado_do_recurso_texto",
        "resultado_acordao",
        "resultado_exec_texto"
    ]

    target_candidate_cols = [c for c in target_candidate_cols if c in df.columns]

    target = pd.Series([np.nan] * len(df), index=df.index)
    source = pd.Series([None] * len(df), index=df.index)

    for col in target_candidate_cols:
        temp = df[col].apply(classify_outcome_text)
        temp = pd.Series(temp, index=df.index)

        mask = target.isna() & temp.notna()
        target.loc[mask] = temp.loc[mask]
        source.loc[mask] = col

    out = df[[PROCESS_ID_COL]].copy()
    out[TARGET_COL] = target
    out["target_source"] = source

    return out


# =============================================================================
# 5. ANÁLISE DE RELAÇÃO COM TARGET
# =============================================================================

def target_rate_by_category(df, col, target_col=TARGET_COL, min_count=30):
    """
    Calcula taxa de perda por categoria.
    """
    result = (
        df
        .groupby(col, dropna=False)
        .agg(
            qtd_processos=(target_col, "count"),
            qtd_perdas=(target_col, "sum"),
            taxa_perda=(target_col, "mean")
        )
        .reset_index()
    )

    result = result[result["qtd_processos"] >= min_count]
    result = result.sort_values(["taxa_perda", "qtd_processos"], ascending=[False, False])

    return result


def analyze_event_flags_vs_target(df):
    """
    Analisa diferença de taxa de perda para flags de eventos.
    """
    flag_cols = [c for c in df.columns if c.startswith("flag_teve_")]

    flag_analysis = []

    for col in flag_cols:
        temp = (
            df
            .groupby(col)
            .agg(
                qtd_processos=(TARGET_COL, "count"),
                taxa_perda=(TARGET_COL, "mean")
            )
            .reset_index()
        )

        if len(temp) > 1:
            taxa_0 = temp.loc[temp[col] == 0, "taxa_perda"].values
            taxa_1 = temp.loc[temp[col] == 1, "taxa_perda"].values

            flag_analysis.append({
                "feature": col,
                "qtd_com_flag": int((df[col] == 1).sum()),
                "perc_com_flag": float((df[col] == 1).mean()),
                "taxa_perda_sem_flag": float(taxa_0[0]) if len(taxa_0) else np.nan,
                "taxa_perda_com_flag": float(taxa_1[0]) if len(taxa_1) else np.nan,
                "diferenca_taxa_perda": float(taxa_1[0] - taxa_0[0]) if len(taxa_0) and len(taxa_1) else np.nan
            })

    if not flag_analysis:
        return pd.DataFrame()

    return pd.DataFrame(flag_analysis).sort_values("diferenca_taxa_perda", ascending=False)


# =============================================================================
# 6. PIPELINE PRINCIPAL
# =============================================================================

def main():
    print("\n" + "#" * 100)
    print("INÍCIO DA EDA FORENSE JURÍDICA")
    print("#" * 100)

    # -------------------------------------------------------------------------
    # 6.1 Leitura das bases
    # -------------------------------------------------------------------------
    print("\n[1/10] Lendo base de processos...")
    df_processos = read_data(PROCESSOS_FILE)
    print(f"Processos: {df_processos.shape}")

    print("\n[2/10] Lendo base de eventos...")

    # Lê apenas as colunas necessárias se possível.
    event_cols = [PROCESS_ID_COL, EVENT_NUM_COL, EVENT_TYPE_COL, EVENT_TEXT_COL, EVENT_DATE_COL]

    try:
        df_eventos = read_data(EVENTOS_FILE, columns=event_cols)
    except Exception as e:
        print("Não foi possível ler somente as colunas configuradas.")
        print("Tentando ler a base completa de eventos...")
        print(f"Erro original: {e}")
        df_eventos = read_data(EVENTOS_FILE)

    print(f"Eventos: {df_eventos.shape}")

    # -------------------------------------------------------------------------
    # 6.2 Auditoria estrutural
    # -------------------------------------------------------------------------
    print("\n[3/10] Gerando overview estrutural...")
    overview_processos = basic_overview(df_processos, "processos")
    overview_eventos = basic_overview(df_eventos, "eventos")

    save_report(overview_processos, "overview_processos.csv")
    save_report(overview_eventos, "overview_eventos.csv")

    print("\nAuditando chave da base de processos...")
    duplicados_processos = key_audit(df_processos, PROCESS_ID_COL, "processos")
    save_report(duplicados_processos, "duplicados_chave_processos.csv")

    print("\nAuditando chave da base de eventos...")
    # Na base de eventos esperamos repetição de numero_processo.
    eventos_por_processo = (
        df_eventos
        .groupby(PROCESS_ID_COL)
        .size()
        .reset_index(name="qtd_eventos")
        .sort_values("qtd_eventos", ascending=False)
    )
    save_report(eventos_por_processo, "eventos_por_processo.csv")

    rel_audit, processos_sem_eventos, eventos_sem_processo = process_event_relationship_audit(
        df_processos,
        df_eventos,
        PROCESS_ID_COL
    )
    save_report(rel_audit, "auditoria_processos_eventos.csv")

    pd.DataFrame({PROCESS_ID_COL: list(processos_sem_eventos)}).to_csv(
        REPORTS_DIR / "processos_sem_eventos.csv",
        index=False
    )

    pd.DataFrame({PROCESS_ID_COL: list(eventos_sem_processo)}).to_csv(
        REPORTS_DIR / "eventos_sem_processo.csv",
        index=False
    )

    # -------------------------------------------------------------------------
    # 6.3 Nulos, cardinalidade e dominância
    # -------------------------------------------------------------------------
    print("\n[4/10] Gerando relatórios de qualidade...")

    null_processos = null_report(df_processos)
    null_processos["faixa_nulos"] = null_processos["perc_nulos"].apply(classify_null_severity)
    save_report(null_processos, "null_report_processos.csv")

    null_eventos = null_report(df_eventos)
    null_eventos["faixa_nulos"] = null_eventos["perc_nulos"].apply(classify_null_severity)
    save_report(null_eventos, "null_report_eventos.csv")

    card_processos = cardinality_report(df_processos)
    save_report(card_processos, "cardinality_report_processos.csv")

    card_eventos = cardinality_report(df_eventos)
    save_report(card_eventos, "cardinality_report_eventos.csv")

    dominant_processos = dominant_value_report(df_processos)
    save_report(dominant_processos, "dominant_report_processos.csv")

    dominant_eventos = dominant_value_report(df_eventos)
    save_report(dominant_eventos, "dominant_report_eventos.csv")

    numeric_processos = numeric_summary(df_processos)
    save_report(numeric_processos, "numeric_summary_processos.csv")

    date_processos = date_report(df_processos)
    save_report(date_processos, "date_report_processos.csv")

    date_eventos = date_report(df_eventos)
    save_report(date_eventos, "date_report_eventos.csv")

    # -------------------------------------------------------------------------
    # 6.4 Perfil forense das colunas de processos
    # -------------------------------------------------------------------------
    print("\n[5/10] Classificando colunas da base de processos...")

    column_groups = pd.DataFrame({"coluna": df_processos.columns})
    column_groups["grupo_inferido"] = column_groups["coluna"].apply(classify_column_by_name)
    save_report(column_groups, "processos_column_groups.csv")

    external_pred_cols = identify_external_prediction_cols(df_processos.columns)
    deprecated_cols = identify_deprecated_cols(df_processos.columns)
    link_cols = identify_link_cols(df_processos.columns)
    long_text_cols = identify_long_text_cols(df_processos.columns)
    post_decision_cols = identify_result_or_post_decision_cols(df_processos.columns)

    processos_profile = (
        null_processos
        .merge(card_processos[["coluna", "qtd_distintos", "perc_distintos"]], on="coluna", how="left")
        .merge(dominant_processos[["coluna", "valor_mais_frequente", "perc_valor_mais_frequente"]], on="coluna", how="left")
        .merge(column_groups, on="coluna", how="left")
    )

    processos_profile["recomendacao_uso"] = processos_profile.apply(
        lambda row: recommend_column_usage(
            row,
            external_pred_cols=external_pred_cols,
            deprecated_cols=deprecated_cols,
            link_cols=link_cols,
            long_text_cols=long_text_cols,
            post_decision_cols=post_decision_cols
        ),
        axis=1
    )

    processos_profile = processos_profile.sort_values(
        ["grupo_inferido", "perc_nulos"],
        ascending=[True, False]
    )

    save_report(processos_profile, "processos_profile_com_recomendacao.csv")

    leakage_reference = pd.DataFrame({
        "coluna": (
            external_pred_cols
            + deprecated_cols
            + link_cols
            + long_text_cols
            + post_decision_cols
        )
    }).drop_duplicates()

    save_report(leakage_reference, "colunas_candidatas_leakage_ou_remocao.csv")

    # -------------------------------------------------------------------------
    # 6.5 Tratamento inicial da base de eventos
    # -------------------------------------------------------------------------
    print("\n[6/10] Tratando coluna tipo dos eventos...")

    required_event_cols = [PROCESS_ID_COL, EVENT_TYPE_COL, EVENT_DATE_COL]
    missing_event_cols = [c for c in required_event_cols if c not in df_eventos.columns]

    if missing_event_cols:
        raise KeyError(f"Colunas obrigatórias ausentes na base de eventos: {missing_event_cols}")

    df_eventos[EVENT_DATE_COL] = pd.to_datetime(df_eventos[EVENT_DATE_COL], errors="coerce")
    df_eventos["tipo_clean"] = df_eventos[EVENT_TYPE_COL].map(normalize_text)
    df_eventos["tipo_categoria"] = df_eventos["tipo_clean"].map(categorize_event_type)

    # Salva eventos tratados.
    eventos_tratados_path = PROCESSED_DIR / "eventos_tratados_eda.parquet"
    df_eventos.to_parquet(eventos_tratados_path, index=False)
    print(f"Eventos tratados salvos em: {eventos_tratados_path}")

    # -------------------------------------------------------------------------
    # 6.6 Frequência dos eventos
    # -------------------------------------------------------------------------
    print("\n[7/10] Gerando relatórios dos eventos...")

    event_type_freq = (
        df_eventos["tipo_clean"]
        .value_counts(dropna=False)
        .reset_index()
    )
    event_type_freq.columns = ["tipo_clean", "qtd_eventos"]
    event_type_freq["perc_eventos"] = event_type_freq["qtd_eventos"] / len(df_eventos)
    event_type_freq["perc_acumulado"] = event_type_freq["perc_eventos"].cumsum()
    save_report(event_type_freq, "event_type_frequency_report.csv")

    event_category_freq = (
        df_eventos["tipo_categoria"]
        .value_counts(dropna=False)
        .reset_index()
    )
    event_category_freq.columns = ["tipo_categoria", "qtd_eventos"]
    event_category_freq["perc_eventos"] = event_category_freq["qtd_eventos"] / len(df_eventos)
    event_category_freq["perc_acumulado"] = event_category_freq["perc_eventos"].cumsum()
    save_report(event_category_freq, "event_category_frequency_report.csv")

    event_category_samples = sample_event_types_by_category(df_eventos)
    save_report(event_category_samples, "event_category_samples.csv")

    event_date_report = pd.DataFrame({
        "min_data_evento": [df_eventos[EVENT_DATE_COL].min()],
        "max_data_evento": [df_eventos[EVENT_DATE_COL].max()],
        "qtd_eventos": [len(df_eventos)],
        "qtd_eventos_sem_data": [int(df_eventos[EVENT_DATE_COL].isna().sum())],
        "perc_eventos_sem_data": [df_eventos[EVENT_DATE_COL].isna().mean()]
    })
    save_report(event_date_report, "event_date_report.csv")

    df_eventos["ano_mes_evento"] = df_eventos[EVENT_DATE_COL].dt.to_period("M").astype(str)

    events_by_month = (
        df_eventos
        .groupby("ano_mes_evento")
        .size()
        .reset_index(name="qtd_eventos")
        .sort_values("ano_mes_evento")
    )
    save_report(events_by_month, "events_by_month.csv")

    # -------------------------------------------------------------------------
    # 6.7 Primeira camada de features de eventos para ABT exploratória
    # -------------------------------------------------------------------------
    print("\n[8/10] Criando primeira camada de features de eventos...")

    # Garantir ordenação
    sort_cols = [PROCESS_ID_COL, EVENT_DATE_COL]
    if EVENT_NUM_COL in df_eventos.columns:
        sort_cols.append(EVENT_NUM_COL)

    df_eventos = df_eventos.sort_values(sort_cols)

    features_eventos_basicas = build_basic_event_features(df_eventos)
    features_primeiro_ultimo = build_first_last_event_features(df_eventos)
    features_eventos_categoria = build_event_category_features(df_eventos)

    features_eventos = (
        features_eventos_basicas
        .merge(features_primeiro_ultimo, on=PROCESS_ID_COL, how="left")
        .merge(features_eventos_categoria, on=PROCESS_ID_COL, how="left")
    )

    if features_eventos[PROCESS_ID_COL].nunique() != len(features_eventos):
        raise ValueError("Features de eventos duplicaram processos. Verifique o grão.")

    features_eventos_path = PROCESSED_DIR / "features_eventos_eda_inicial.parquet"
    features_eventos.to_parquet(features_eventos_path, index=False)
    print(f"Features iniciais de eventos salvas em: {features_eventos_path}")

    # -------------------------------------------------------------------------
    # 6.8 Construção da ABT exploratória
    # -------------------------------------------------------------------------
    print("\n[9/10] Construindo ABT exploratória...")

    df_abt_eda = df_processos.merge(
        features_eventos,
        on=PROCESS_ID_COL,
        how="left"
    )

    if len(df_abt_eda) != len(df_processos):
        print("ATENÇÃO: O merge alterou a quantidade de linhas.")
        print(f"Linhas processos: {len(df_processos):,}")
        print(f"Linhas ABT: {len(df_abt_eda):,}")

    df_abt_eda["flag_tem_eventos"] = df_abt_eda["qtd_eventos"].notna().astype(int)

    event_count_cols = [
        c for c in df_abt_eda.columns
        if c.startswith("qtd_evento_cat_") or c.startswith("flag_teve_")
    ]

    if event_count_cols:
        df_abt_eda[event_count_cols] = df_abt_eda[event_count_cols].fillna(0)

    # Target inicial
    target_df = build_initial_target(df_abt_eda)

    df_abt_eda = df_abt_eda.merge(
        target_df,
        on=PROCESS_ID_COL,
        how="left"
    )

    target_distribution = (
        df_abt_eda[TARGET_COL]
        .value_counts(dropna=False)
        .reset_index()
    )
    target_distribution.columns = [TARGET_COL, "qtd"]
    target_distribution["perc"] = target_distribution["qtd"] / len(df_abt_eda)
    save_report(target_distribution, "target_distribution_inicial.csv")

    abt_path = PROCESSED_DIR / "abt_eda_inicial.parquet"
    df_abt_eda.to_parquet(abt_path, index=False)
    print(f"ABT exploratória salva em: {abt_path}")

    # -------------------------------------------------------------------------
    # 6.9 Análise inicial entre features e target
    # -------------------------------------------------------------------------
    print("\n[10/10] Analisando relação inicial entre features e target...")

    df_model_eda = df_abt_eda[df_abt_eda[TARGET_COL].notna()].copy()

    if not df_model_eda.empty:
        df_model_eda[TARGET_COL] = df_model_eda[TARGET_COL].astype(int)

        taxa_perda_global = df_model_eda[TARGET_COL].mean()
        print(f"Taxa global de perda no target inicial: {taxa_perda_global:.2%}")

        pd.DataFrame([{
            "taxa_perda_global": taxa_perda_global,
            "qtd_linhas_com_target": len(df_model_eda),
            "qtd_linhas_total": len(df_abt_eda),
            "perc_linhas_com_target": len(df_model_eda) / len(df_abt_eda)
        }]).to_csv(REPORTS_DIR / "target_global_summary.csv", index=False)

        category_cols_to_analyze = [
            "assunto_normalizado_texto",
            "assunto_texto",
            "classe_texto",
            "uf",
            "cidade",
            "vara_texto",
            "orgao_julgador_texto",
            "fase_processual_texto",
            "ultima_categoria_evento"
        ]

        for col in category_cols_to_analyze:
            if col in df_model_eda.columns:
                report = target_rate_by_category(
                    df_model_eda,
                    col,
                    target_col=TARGET_COL,
                    min_count=30
                )

                safe_col = re.sub(r"[^a-zA-Z0-9_]", "_", col)
                save_report(report, f"target_rate_by_{safe_col}.csv")

        flag_analysis_df = analyze_event_flags_vs_target(df_model_eda)
        save_report(flag_analysis_df, "flag_event_analysis.csv")

    else:
        print("Não há linhas com target inicial definido. Pulando análise target × features.")

    print("\n" + "#" * 100)
    print("EDA FORENSE FINALIZADA")
    print("#" * 100)
    print("\nPrincipais saídas:")
    print(f"- {REPORTS_DIR / 'processos_profile_com_recomendacao.csv'}")
    print(f"- {REPORTS_DIR / 'event_type_frequency_report.csv'}")
    print(f"- {REPORTS_DIR / 'event_category_frequency_report.csv'}")
    print(f"- {REPORTS_DIR / 'target_distribution_inicial.csv'}")
    print(f"- {PROCESSED_DIR / 'features_eventos_eda_inicial.parquet'}")
    print(f"- {PROCESSED_DIR / 'abt_eda_inicial.parquet'}")


if __name__ == "__main__":
    main()
'''

path = Path("/mnt/data/eda_forense_juridico.py")
path.write_text(script, encoding="utf-8")

print(f"Arquivo criado: {path}")
print(f"Tamanho: {path.stat().st_size / 1024:.1f} KB")
