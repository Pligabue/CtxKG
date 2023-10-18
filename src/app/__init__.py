from flask import Flask
import secrets

from .controllers import language_bp, home_bp


app = Flask(__name__)
app.register_blueprint(language_bp)
app.register_blueprint(home_bp)
app.secret_key = secrets.token_hex()
