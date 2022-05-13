from flask import Blueprint, render_template

bp = Blueprint('graphs', __name__, url_prefix='/<result>/graphs')

@bp.route("/")
def index(result):
    return f"<p>Graphs {result}</p>"

@bp.route("/base/")
def base(result):
    return f"<p>{result} BASE</p>"

@bp.route("/base/<graph>")
def base_graph(result, graph):
    return f"<p>{result} BASE graph {graph}</p>"

@bp.route("/clean/")
def clean(result):
    return f"<p>{result} CLEAN</p>"

@bp.route("/clean/<graph>")
def clean_graph(result, graph):
    return f"<p>{result} clean graph {graph}</p>"
