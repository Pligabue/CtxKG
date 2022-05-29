from flask import Blueprint, jsonify, render_template
import json
from pathlib import Path

RESULT_DIR = Path("results")

bp = Blueprint('graphs', __name__, url_prefix='/<result>/graphs')

@bp.route("/base/")
def base(result):
    graphs = (RESULT_DIR / result / "base").glob("*.json")
    return render_template("results/graphs/base.j2", result=result, graphs=graphs)

@bp.route("/base/<graph>/")
def base_graph(result, graph):
    graph_path = RESULT_DIR / result / "base" / graph
    return render_template("results/graphs/base_graph.j2", result=result, graph=graph, graph_path=graph_path)

@bp.route("/base/<graph>/json/")
def base_graph_json(result, graph):
    graph = RESULT_DIR / result / "base" / graph
    with graph.open() as f:
        return jsonify(json.load(f))

@bp.route("/clean/")
def clean(result):
    graphs = (RESULT_DIR / result / "clean").glob("*.json")
    return render_template("results/graphs/clean.j2", result=result, graphs=graphs)

@bp.route("/clean/<graph>/")
def clean_graph(result, graph):
    graph_path = RESULT_DIR / result / "clean" / graph
    return render_template("results/graphs/clean_graph.j2", result=result, graph=graph, graph_path=graph_path)

@bp.route("/clean/<graph>/json/")
def clean_graph_json(result, graph):
    graph = RESULT_DIR / result / "clean" / graph
    with graph.open() as f:
        return jsonify(json.load(f))