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
            "entities": {entity_id: entity_label for entity_id, entity_label in graph["entities"].items() if entity_id in expanded_nodes},
            "graph": [triple for triple in graph["graph"] if triple["subject_id"] in expanded_nodes],
            "links": {node: [linked_node for linked_node in linked_nodes if linked_node in expanded_nodes] for node, linked_nodes in graph["links"].items() if node in expanded_nodes}
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