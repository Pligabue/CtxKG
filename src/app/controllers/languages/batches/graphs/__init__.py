from flask import Blueprint, jsonify, render_template
import json
from pathlib import Path

from ......constants import GRAPH_DIR

bp = Blueprint('graphs', __name__, url_prefix='/<batch>/graphs')


@bp.route("/base/", defaults={"version": "base"})
@bp.route("/clean/", defaults={"version": "clean"})
def index(language, batch, version):
    graphs = (GRAPH_DIR / language / batch / version).glob("*.json")
    return render_template(
        "batches/graphs/index.j2",
        language=language,
        batch=batch,
        version=version,
        graphs=graphs,
        title=f"{version.capitalize()} Graphs"
    )


@bp.route("/base/<graph>/", defaults={"version": "base"})
@bp.route("/clean/<graph>/", defaults={"version": "clean"})
def graph(language, batch, version, graph):
    graph_path = GRAPH_DIR / language / batch / version / graph
    return render_template(
        "batches/graphs/graph.j2",
        language=language,
        batch=batch,
        version=version,
        graph=graph,
        graph_path=graph_path,
        title=f"{version.capitalize()} Graphs",
        subtitle=f"{version.capitalize()} {graph_path.stem}"
    )


@bp.route("/base/<graph>/json/", defaults={"version": "base"})
@bp.route("/clean/<graph>/json/", defaults={"version": "clean"})
def graph_json(language, batch, version, graph):
    graph = GRAPH_DIR / language / batch / version / graph
    with graph.open(encoding="utf-8") as f:
        return jsonify(json.load(f))


@bp.route("/base/<graph>/bridges/<node>/", defaults={"version": "base"})
@bp.route("/clean/<graph>/bridges/<node>/", defaults={"version": "clean"})
def node_bridges(language, batch, version, graph, node):
    bridges = {}
    bridge_path = GRAPH_DIR / language / batch / version / "bridges" / graph
    with bridge_path.open(encoding="utf-8") as f:
        all_bridges = json.load(f)
        for target_graph, target_graph_bridges in all_bridges.items():
            if node in target_graph_bridges:
                bridges[target_graph] = target_graph_bridges[node]
    return jsonify(bridges)


@bp.route("/base/<graph>/<node>/", defaults={"version": "base"})
@bp.route("/clean/<graph>/<node>/", defaults={"version": "clean"})
def expand_node(language, batch, version, graph, node):
    graph_path = GRAPH_DIR / language / batch / version / graph
    with graph_path.open(encoding="utf-8") as f:
        graph = json.load(f)
        expanded_nodes = get_expanded_nodes(graph, node)

        links = {}
        for node, linked_nodes in graph["links"].items():
            if node in expanded_nodes:
                links[node] = [ln for ln in linked_nodes if ln in expanded_nodes]

        expanded_node_json = {
            "entities": {e_id: e_label for e_id, e_label in graph["entities"].items() if e_id in expanded_nodes},
            "graph": [triple for triple in graph["graph"] if triple["subject_id"] in expanded_nodes],
            "links": links,
        }
        return jsonify(expanded_node_json)


def get_expanded_nodes(graph, initial_node):
    explored = set()
    entities = {initial_node}
    while len(explored) != len(entities):
        to_explore = {e for e in entities if e not in explored}
        new_entities = set()
        for e in to_explore:
            e_triples = [t for t in graph["graph"] if e == t["subject_id"] or e == t["object_id"]]
            e_expanded_entities = {t["object_id"] if e == t["subject_id"] else t["subject_id"] for t in e_triples}
            e_new_entities = {e for e in e_expanded_entities if e not in to_explore and e not in explored}
            new_entities.update(e_new_entities)
        entities.update(new_entities)
        explored.update(to_explore)

    return entities


@bp.route("/base/<graph>/document/", defaults={"version": "base"})
@bp.route("/clean/<graph>/document/", defaults={"version": "clean"})
def get_original_document(language, batch, version, graph):
    graph_path = GRAPH_DIR / language / batch / version / graph
    with graph_path.open(encoding="utf-8") as f:
        graph = json.load(f)
    document_file = Path(graph["document"])
    with document_file.open(encoding="utf-8") as f:
        document_text = f.read()
    return jsonify(document_text)
