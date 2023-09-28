from flask import Blueprint, render_template
from pathlib import Path

from .batches import bp as batch_bp


bp = Blueprint('languages', __name__, url_prefix='/<language>')
bp.register_blueprint(batch_bp)
