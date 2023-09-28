from flask import Blueprint, render_template

from .graphs import bp as graph_bp, GRAPH_DIR

bp = Blueprint('batches', __name__, url_prefix='/batches')
bp.register_blueprint(graph_bp)


@bp.route("/")
def index(language):
    target_dir = GRAPH_DIR / language
    batches = [path for path in target_dir.iterdir() if path.is_dir()]
    return render_template("batches/index.j2", language=language, batches=batches)


@bp.route("/<batch>/")
def batch(language, batch):
    base_graphs = (GRAPH_DIR / language / batch / "base").glob("*.json")
    clean_graphs = (GRAPH_DIR / language/ batch / "clean").glob("*.json")
    return render_template("batches/batch.j2", language=language, batch=batch, base_graphs=base_graphs, clean_graphs=clean_graphs)
