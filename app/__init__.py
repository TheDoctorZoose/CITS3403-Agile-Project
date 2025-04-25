
from flask import Flask, render_template

from flask import Flask, render_template

def create_app():
    app = Flask(__name__)

    @app.route('/')
    def index():
        return render_template("index.html")

    @app.route('/login')
    def login():
        return render_template("login.html")

    @app.route('/register')
    def register():
        return render_template("createaccount.html")

    @app.route('/forgot-password')
    def forgot_password():
        return render_template("forgotpassword.html")

    @app.route('/intro')
    def intro():
        return render_template("intropage.html")

    @app.route('/forum')
    def forum():
        return render_template("forum.html")

    return app
