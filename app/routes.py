import io
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from app.models import User, GameEntry, Comment, Like, Favorite

from app.forms import RegistrationForm, LoginForm
from app import db 

from datetime import datetime

from io import TextIOWrapper

import csv, json

from app.models import RawCSVEntry

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template("index.html")

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.homepage'))  # or wherever

    form = RegistrationForm()

    if form.validate_on_submit():
        existing_user = User.query.filter(
            (User.username == form.username.data) | (User.email == form.email.data)
        ).first()

        if existing_user:
            flash('Username or email already exists. Please choose another.', 'error')
        else:
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful. You can now log in.', 'success')
            return redirect(url_for('main.login'))

    return render_template('createaccount.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash("Logged in successfully.", "success")
            return redirect(url_for('main.index'))
        else:
            flash("Invalid email or password. Please try again.", "danger")

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

# @main.route('/forum')
# def forum():
#     return render_template("upload-data-view.html")

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

@main.route('/forum', methods=['GET', 'POST'])
@login_required
def forum():
    if request.method == 'POST':
        game_title = request.form.get('gameTitle')
        date_str = request.form.get('datePlayed')

        try:
            date_played = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid date format.", "error")
            return redirect(url_for('main.forum'))

        new_entry = GameEntry(
            game_title=game_title,
            date_played=date_played,  
            user_id=current_user.id
        )
        db.session.add(new_entry)
        db.session.commit()
        flash('Entry submitted!')

        return redirect(url_for('main.forum'))

    entries_raw = GameEntry.query.order_by(GameEntry.timestamp.desc()).all()

    entries = []
    for entry in entries_raw:
        entries.append({
            'entry': entry,
            'like_count': entry.likes.count(),
            'favorite_count': entry.favorites.count(),
            'liked': Like.query.filter_by(user_id=current_user.id, entry_id=entry.id).first() is not None,
            'favorited': Favorite.query.filter_by(user_id=current_user.id, entry_id=entry.id).first() is not None,
        })

    return render_template('upload-data-view.html', entries=entries)


@main.route('/forum/<int:entry_id>', methods=['GET', 'POST'])
@login_required
def view_entry(entry_id):
    entry = GameEntry.query.get_or_404(entry_id)

    if request.method == 'POST':
        comment_text = request.form.get('comment')
        if comment_text:
            comment = Comment(
                content=comment_text,
                user_id=current_user.id,
                entry_id=entry.id
            )
            db.session.add(comment)
            db.session.commit()
            flash('Comment posted!')

        return redirect(url_for('main.view_entry', entry_id=entry.id))

    return render_template('entry_detail.html', entry=entry)

@main.route('/upload_csv', methods=['POST'])
@login_required
def upload_csv():
    file = request.files['file']
    if file and file.filename.endswith('.csv'):
        try:
            stream = io.StringIO(file.stream.read().decode('utf-8'))
        except UnicodeDecodeError:
            stream = io.StringIO(file.stream.read().decode('ISO-8859-1'))

        reader = csv.reader(stream)
        for row in reader:
            entry = RawCSVEntry(
                raw_data=",".join(row),
                user_id=current_user.id
            )
            db.session.add(entry)
        db.session.commit()
        flash("CSV uploaded successfully.")
    else:
        flash("Please upload a valid CSV file.")
    return redirect(url_for('main.forum'))



@main.route('/upload_json', methods=['POST'])
@login_required
def upload_json():
    file = request.files['file']
    if file and file.filename.endswith('.json'):
        data = json.load(file.stream)
        for item in data:
            entry = GameEntry(
                game_title=item['game_title'],
                date_played=datetime.strptime(item['date_played'], "%Y-%m-%d").date(),
                user_id=current_user.id
            )
            db.session.add(entry)
        db.session.commit()
        flash("JSON uploaded successfully.")
    return redirect(url_for('main.forum'))
from flask import jsonify, request

@main.route('/like/<int:entry_id>', methods=['POST'])
@login_required
def like_entry(entry_id):
    entry = GameEntry.query.get_or_404(entry_id)
    existing_like = Like.query.filter_by(user_id=current_user.id, entry_id=entry_id).first()

    liked = False
    if existing_like:
        db.session.delete(existing_like)
    else:
        new_like = Like(user_id=current_user.id, entry_id=entry_id)
        db.session.add(new_like)
        liked = True

    db.session.commit()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'liked': liked,
            'like_count': entry.likes.count()
        })

    # Fallback for non-AJAX
    flash("You liked this entry!" if liked else "You unliked this entry.", "success" if liked else "info")
    return redirect(url_for('main.forum'))

@main.route('/favorite/<int:entry_id>', methods=['POST'])
@login_required
def favorite_entry(entry_id):
    entry = GameEntry.query.get_or_404(entry_id)
    existing_favorite = Favorite.query.filter_by(user_id=current_user.id, entry_id=entry_id).first()

    favorited = False
    if existing_favorite:
        db.session.delete(existing_favorite)
    else:
        new_favorite = Favorite(user_id=current_user.id, entry_id=entry_id)
        db.session.add(new_favorite)
        favorited = True

    db.session.commit()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'favorited': favorited,
            'favorite_count': entry.favorites.count()
        })

    # Fallback for non-AJAX
    flash("Added to favorites!" if favorited else "Removed from favorites.", "success" if favorited else "info")
    return redirect(url_for('main.forum'))


@main.route('/delete_entry/<int:entry_id>', methods=['POST'])
@login_required
def delete_entry(entry_id):
    entry = GameEntry.query.get_or_404(entry_id)

    if entry.user_id != current_user.id:
        flash("You are not authorized to delete this entry.", "error")
        return redirect(url_for('main.forum'))

    db.session.delete(entry)
    db.session.commit()
    flash("Entry deleted successfully.", "success")
    return redirect(url_for('main.forum'))



@main.route('/auth', methods=['GET'])
def auth():
    login_form = LoginForm()
    register_form = RegistrationForm()
    return render_template('auth.html', login_form=login_form, register_form=register_form)