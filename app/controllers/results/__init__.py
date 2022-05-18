from flask import Blueprint, render_template

from .graphs import bp as graph_bp, RESULT_DIR

bp = Blueprint('results', __name__, url_prefix='/results')
bp.register_blueprint(graph_bp)

@bp.route("/")
def index():
    results = [path for path in RESULT_DIR.iterdir() if path.is_dir()]
    return render_template("results/index.j2", results=results)

@bp.route("/<result>/")
def result(result):
    base_graphs =  (RESULT_DIR / result / "base").glob("*.json")
    clean_graphs = (RESULT_DIR / result / "clean").glob("*.json")
    return render_template("results/result.j2", result=result, base_graphs=base_graphs, clean_graphs=clean_graphs)