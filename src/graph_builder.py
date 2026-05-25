# src/graph_builder.py

import os
import networkx as nx
from pyvis.network import Network
from src.config import GRAPH_FEATURES


def make_node_id(node_type, value):
    value = str(value).strip().replace(" ", "_")
    return f"{node_type}::{value}"


def build_case_graph(df, max_rows=None):
    """
    Cria grafo heterogêneo:
    processo -> entidades estruturadas.
    """
    if max_rows:
        df = df.head(max_rows)

    G = nx.Graph()

    for _, row in df.iterrows():
        process_number = row.get("process_number_norm")

        if not process_number:
            continue

        process_node = make_node_id("processo", process_number)

        G.add_node(
            process_node,
            label=str(row.get("process_number", process_number)),
            node_type="processo",
            title=f"Processo: {row.get('process_number', process_number)}",
        )

        for feature in GRAPH_FEATURES:
            if feature not in df.columns:
                continue

            value = row.get(feature)

            if value is None or str(value).strip() == "" or str(value).upper() == "NAN":
                continue

            entity_node = make_node_id(feature, value)

            G.add_node(
                entity_node,
                label=str(value),
                node_type=feature,
                title=f"{feature}: {value}",
            )

            G.add_edge(
                process_node,
                entity_node,
                edge_type=f"tem_{feature}",
                weight=1,
            )

    return G


def get_local_subgraph(G, process_number_norm, depth=1, max_nodes=150):
    """
    Retorna subgrafo local ao redor de um processo.
    """
    process_node = make_node_id("processo", process_number_norm)

    if process_node not in G:
        return nx.Graph()

    nodes = {process_node}
    frontier = {process_node}

    for _ in range(depth):
        new_frontier = set()

        for node in frontier:
            new_frontier.update(G.neighbors(node))

        nodes.update(new_frontier)
        frontier = new_frontier

        if len(nodes) >= max_nodes:
            break

    nodes = list(nodes)[:max_nodes]
    return G.subgraph(nodes).copy()


def render_graph_pyvis(G, output_path="outputs/graphs/graph.html"):
    """
    Renderiza o grafo em HTML usando PyVis.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    net = Network(
        height="700px",
        width="100%",
        bgcolor="#ffffff",
        font_color="#222222",
        notebook=False,
    )

    color_map = {
        "processo": "#1f77b4",
        "produto": "#ff7f0e",
        "carteira": "#2ca02c",
        "fase": "#d62728",
        "estimativa_perda": "#9467bd",
        "escritorio": "#8c564b",
        "advogado": "#e377c2",
        "comarca": "#7f7f7f",
        "uf": "#bcbd22",
        "vara": "#17becf",
        "status": "#aec7e8",
        "fase_processual": "#ffbb78",
    }

    for node, attrs in G.nodes(data=True):
        node_type = attrs.get("node_type", "default")

        size = 25 if node_type == "processo" else 12
        color = color_map.get(node_type, "#cccccc")

        net.add_node(
            node,
            label=attrs.get("label", node),
            title=attrs.get("title", node),
            color=color,
            size=size,
        )

    for source, target, attrs in G.edges(data=True):
        net.add_edge(
            source,
            target,
            title=attrs.get("edge_type", ""),
            value=attrs.get("weight", 1),
        )

    net.force_atlas_2based()
    net.show_buttons(filter_=["physics"])
    net.write_html(output_path)

    return output_path