from flask import Blueprint, request, render_template, url_for, redirect, flash

from ....constants import GRAPH_DIR
from ....utils.batch_data.helpers import get_batch_list, pause_batch, delete_batch
from ...forms.batch import BatchForm
from ...tasks.create_batch import create_batch
from ...tasks.resume_processing import resume_processing
from .graphs import bp as graph_bp

from ....utils.batch_data.types import BlabKGException


bp = Blueprint('batches', __name__, url_prefix='/<language>/batches')
bp.register_blueprint(graph_bp)


@bp.route("/")
def index(language):
    batches = get_batch_list(language)
    return render_template("batches/index.j2", language=language, batches=batches)


@bp.route("/new/")
@bp.post("/new/")
def new(language):
    form = BatchForm(request.form)
    form.language.process_data(language)
    if request.method == "POST" and form.validate():
        create_batch(
            language=language,
            batch=form.name.data,  # type: ignore
            files=request.files.getlist(form.filenames.name),
            size=form.bert_size.data,
            extraction_model=form.extraction_model.data,
            ratio=form.embedding_ratio.data,  # type: ignore
            similarity_threshold=form.similarity_threshold.data,  # type: ignore
            bridge_threshold=form.bridge_threshold.data,  # type: ignore
            batch_size=form.processing_batch_size.data,  # type: ignore
        )
        return redirect(url_for(".index", language=language))
    return render_template("batches/new.j2", language=language, form=form)


@bp.route("/<batch>/pause/")
def pause(language, batch):
    pause_batch(language, batch)
    return redirect(url_for(".index", language=language))


@bp.route("/<batch>/resume/")
def resume(language, batch):
    resume_processing(language, batch)
    return redirect(url_for(".index", language=language))


@bp.route("/<batch>/delete/")
def delete(language, batch):
    try:
        delete_batch(language, batch)
    except BlabKGException as e:
        flash(str(e), "error")
    return redirect(url_for(".index", language=language))


@bp.route("/<batch>/")
def batch(language, batch):
    base_graphs = (GRAPH_DIR / language / batch / "base").glob("*.json")
    clean_graphs = (GRAPH_DIR / language / batch / "clean").glob("*.json")
    return render_template(
        "batches/batch.j2",
        language=language,
        batch=batch,
        base_graphs=base_graphs,
        clean_graphs=clean_graphs,
    )
