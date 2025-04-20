
from flask import Flask, render_template

def create_app():
    app = Flask(__name__)

    @app.route('/')
    def index():
        return render_template("forum.html")  # 加载 templates/form.html

    return app
