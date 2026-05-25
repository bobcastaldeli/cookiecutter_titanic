# app.py

import streamlit as st
import streamlit.components.v1 as components

from src.data_loader import load_and_prepare_data
from src.preprocessing import normalize_process_number
from src.graph_builder import build_case_graph, get_local_subgraph, render_graph_pyvis
from src.similarity import get_similar_cases


st.set_page_config(
    page_title="MVP Jurimetria - Grafo de Processos",
    layout="wide",
)


st.title("MVP Jurimetria — Grafo de Processos")

st.markdown(
    """
    Este MVP permite consultar um processo, visualizar suas conexões estruturais
    e encontrar processos semelhantes usando dados do Benner e DeepLegal.
    """
)


with st.sidebar:
    st.header("Arquivos")

    benner_file = st.file_uploader(
        "Arquivo Benner",
        type=["csv", "parquet", "xlsx"],
    )

    deeplegal_file = st.file_uploader(
        "Arquivo DeepLegal Processos",
        type=["csv", "parquet", "xlsx"],
    )

    graph_depth = st.slider(
        "Profundidade do grafo",
        min_value=1,
        max_value=3,
        value=1,
    )

    max_nodes = st.slider(
        "Máximo de nós no grafo",
        min_value=30,
        max_value=300,
        value=120,
        step=10,
    )

    top_n_similar = st.slider(
        "Quantidade de processos similares",
        min_value=5,
        max_value=30,
        value=10,
    )


if not benner_file:
    st.warning("Faça upload do arquivo do Benner para começar.")
    st.stop()


# Salva arquivos temporariamente
benner_path = f"data/raw/{benner_file.name}"
with open(benner_path, "wb") as f:
    f.write(benner_file.getbuffer())

deeplegal_path = None

if deeplegal_file:
    deeplegal_path = f"data/raw/{deeplegal_file.name}"
    with open(deeplegal_path, "wb") as f:
        f.write(deeplegal_file.getbuffer())


@st.cache_data
def load_data_cached(benner_path, deeplegal_path):
    return load_and_prepare_data(benner_path, deeplegal_path)


df = load_data_cached(benner_path, deeplegal_path)

st.success(f"Base carregada com {len(df):,} registros.")


with st.expander("Prévia dos dados integrados"):
    st.dataframe(df.head(50), use_container_width=True)


if "process_number_norm" not in df.columns:
    st.error("A base não possui a coluna process_number_norm.")
    st.stop()


process_options = (
    df[["process_number_norm"]]
    .dropna()
    .drop_duplicates()
    .head(5000)["process_number_norm"]
    .tolist()
)

selected_process = st.text_input(
    "Digite o número do processo, com ou sem pontuação",
    value=process_options[0] if process_options else "",
)

selected_process_norm = normalize_process_number(selected_process)


if not selected_process_norm:
    st.warning("Informe um número de processo válido.")
    st.stop()


case_rows = df[df["process_number_norm"] == selected_process_norm]

if case_rows.empty:
    st.error("Processo não encontrado na base.")
    st.stop()


st.header("1. Dados do processo selecionado")

st.dataframe(case_rows.head(10), use_container_width=True)


st.header("2. Grafo local do processo")

with st.spinner("Construindo grafo..."):
    G = build_case_graph(df)
    subgraph = get_local_subgraph(
        G,
        process_number_norm=selected_process_norm,
        depth=graph_depth,
        max_nodes=max_nodes,
    )

    if subgraph.number_of_nodes() == 0:
        st.warning("Não foi possível montar o subgrafo para este processo.")
    else:
        html_path = render_graph_pyvis(subgraph)
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()

        components.html(html, height=750, scrolling=True)

        st.caption(
            f"Grafo com {subgraph.number_of_nodes()} nós e {subgraph.number_of_edges()} arestas."
        )


st.header("3. Processos similares")

with st.spinner("Calculando similaridade estrutural..."):
    similar_cases = get_similar_cases(
        df,
        target_process_number_norm=selected_process_norm,
        top_n=top_n_similar,
    )

if similar_cases.empty:
    st.warning("Nenhum processo similar encontrado.")
else:
    st.dataframe(similar_cases, use_container_width=True)


st.header("4. Diagnóstico rápido da base")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Registros", f"{len(df):,}")

with col2:
    st.metric("Processos únicos", f"{df['process_number_norm'].nunique():,}")

with col3:
    if "produto" in df.columns:
        st.metric("Produtos", f"{df['produto'].nunique():,}")
    else:
        st.metric("Produtos", "N/A")

with col4:
    if "comarca" in df.columns:
        st.metric("Comarcas", f"{df['comarca'].nunique():,}")
    else:
        st.metric("Comarcas", "N/A")