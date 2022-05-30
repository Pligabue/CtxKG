from flask import Blueprint, jsonify, render_template
import json
from pathlib import Path

RESULT_DIR = Path("results")

bp = Blueprint('graphs', __name__, url_prefix='/<result>/graphs')

@bp.route("/base/", defaults={"version": "base"})
@bp.route("/clean/", defaults={"version": "clean"})
def index(result, version):
    graphs = (RESULT_DIR / result / version).glob("*.json")
    return render_template("results/graphs/index.j2",
        result=result,
        version=version,
        graphs=graphs,
        title=f"{version.capitalize()} Graphs"
    )

@bp.route("/base/<graph>/", defaults={"version": "base"})
@bp.route("/clean/<graph>/", defaults={"version": "clean"})
def graph(result, version, graph):
    graph_path = RESULT_DIR / result / version / graph
    return render_template("results/graphs/graph.j2",
        result=result,
        version=version,
        graph=graph,
        graph_path=graph_path,
        title=f"{version.capitalize()} Graphs",
        subtitle=f"{version.capitalize()} {graph_path.stem}"
    )

@bp.route("/base/<graph>/json/", defaults={"version": "base"})
@bp.route("/clean/<graph>/json/", defaults={"version": "clean"})
def graph_json(result, version, graph):
    graph = RESULT_DIR / result / version / graph
    with graph.open() as f:
        return jsonify(json.load(f))

@bp.route("/base/<graph>/bridges/<node>/", defaults={"version": "base"})
@bp.route("/clean/<graph>/bridges/<node>/", defaults={"version": "clean"})
def node_bridges(result, version, graph, node):
    bridges = {}
    bridge_path = RESULT_DIR / result / version / "bridges" / graph
    with bridge_path.open() as f:
        all_bridges = json.load(f)
        for target_graph, target_graph_bridges in all_bridges.items():
            if node in target_graph_bridges:
                bridges[target_graph] = target_graph_bridges[node]
    return jsonify(bridges)

@bp.route("/base/<graph>/<node>/", defaults={"version": "base"})
@bp.route("/clean/<graph>/<node>/", defaults={"version": "clean"})
def expand_node(result, version, graph, node):
    graph_path = RESULT_DIR / result / version / graph
    with graph_path.open() as f:
        graph = json.load(f)
        expanded_nodes = get_expanded_nodes(graph, node)
        expanded_node_json = {
            "graph": [triple for triple in graph["graph"] if triple["subject_id"] in expanded_nodes],
            "links": {node: [linked_node for linked_node in linked_nodes if linked_node in expanded_nodes] for node, linked_nodes in graph["links"].items() if node in expanded_nodes}
        }
        return jsonify(expanded_node_json)

def get_expanded_nodes(graph, initial_node):
    expanded = set()
    to_expand = {initial_node}
    found = set()

    while to_expand:
        for node in to_expand:
            for triple in graph["graph"]:
                if triple["subject_id"] == node:
                    found.add(triple["object_id"])
                if triple["object_id"] == node:
                    found.add(triple["subject_id"])
        expanded.update(to_expand)
        to_expand.update(found)
        found = set()