from flask import Flask
from .controllers import language_bp, home_bp

app = Flask(__name__)
app.register_blueprint(language_bp)
app.register_blueprint(home_bp)
