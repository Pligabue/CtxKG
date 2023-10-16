from flask import Blueprint

from .batches import bp as batch_bp


bp = Blueprint('languages', __name__, url_prefix='/<language>')
bp.register_blueprint(batch_bp)
