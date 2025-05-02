from flask import Blueprint, render_template

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template("index.html")

@main.route('/login')
def login():
    return render_template("login.html")

@main.route('/register')
def register():
    return render_template("createaccount.html")

@main.route('/forgot-password')
def forgot_password():
    return render_template("forgotpassword.html")

@main.route('/intro')
def intro():
    return render_template("intropage.html")

@main.route('/forum')
def forum():
    return render_template("upload-data-view.html")

@main.route('/share')
def share_data_view():
    return render_template("share-data-view.html")

@main.route('/entry')
def entry():
    return render_template("entry.html")

@main.route('/profile')
def profile():
    return render_template("profile.html")

@main.route('/analysis')
def analysis():
    return render_template("analysis.html")
