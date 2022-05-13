from flask import Flask, render_template
from .controllers import result_bp

app = Flask(__name__)
app.register_blueprint(result_bp)

@app.route("/")
def index():
    return render_template("hello.html")
