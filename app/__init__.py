from flask import Flask
from .controllers import result_bp, home_bp

app = Flask(__name__)
app.register_blueprint(result_bp)
app.register_blueprint(home_bp)
