from flask import Blueprint
from .graphs import bp as graph_bp

bp = Blueprint('results', __name__, url_prefix='/results')
bp.register_blueprint(graph_bp)

@bp.route("/")
def index():
    return "<p>Results</p>"

@bp.route("/<result>/")
def result(result):
    return f"<p>Result {result}</p>"