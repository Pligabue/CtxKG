from flask import Flask
import secrets

from .controllers.batches import bp as batch_bp
from .controllers.home import bp as home_bp


app = Flask(__name__)
app.register_blueprint(batch_bp)
app.register_blueprint(home_bp)
app.secret_key = secrets.token_hex()
