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