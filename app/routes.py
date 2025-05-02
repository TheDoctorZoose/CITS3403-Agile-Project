from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from app.models import User
from app.forms import RegistrationForm, LoginForm
from app import db 

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template("index.html")

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("Email already registered.", "error")
            return redirect(url_for('main.register'))

        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data)
        )
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for('main.login'))

    return render_template("createaccount.html", form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=True)
            flash("Logged in successfully.", "success")
            return redirect(url_for('main.index'))
        else:
            flash("Invalid email or password.", "error")
    
    return render_template("login.html", form=form)

@main.route('/logout')
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('main.index'))

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
@login_required
def profile():
    return render_template("profile.html")

@main.route('/analysis')
def analysis():
    return render_template("analysis.html")

@main.route('/visualisation')
def visualisation():
    return render_template("visualisation-options.html")
