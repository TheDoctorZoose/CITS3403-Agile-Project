import io
from os import abort
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify,current_app
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from app.models import FriendRequest, Message, User, GameEntry, Comment, Like, Favorite

from app.forms import RegistrationForm, LoginForm
from app import db , mail

from datetime import datetime

from io import TextIOWrapper

import csv, json

from app.models import RawCSVEntry
from threading import Thread
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message as MailMessage


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

@main.route('/profile/<int:user_id>')
@login_required
def profile(user_id):
    user = User.query.get_or_404(user_id)
    is_own_profile = (user.id == current_user.id)
    posts = GameEntry.query.filter_by(user_id=user.id).order_by(GameEntry.timestamp.desc()).all()

    liked_entries = []
    favorited_entries = []
    if is_own_profile:
        liked_entries = GameEntry.query.join(Like).filter(Like.user_id == user.id).order_by(GameEntry.timestamp.desc()).all()
        favorited_entries = GameEntry.query.join(Favorite).filter(Favorite.user_id == user.id).order_by(GameEntry.timestamp.desc()).all()

    request_sent = FriendRequest.query.filter_by(sender_id=current_user.id, receiver_id=user.id).first()
    are_friends = user in current_user.friends

    friends = user.friends.all() if is_own_profile else None

    return render_template(
        'profile.html',
        user=user,
        posts=posts,
        liked_entries=liked_entries,
        favorited_entries=favorited_entries,
        is_own_profile=is_own_profile,
        request_sent=request_sent,
        are_friends=are_friends,
        friends=friends 
    )


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
        visibility = request.form.get('visibility')  # 👈 新增字段

        try:
            date_played = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid date format.", "error")
            return redirect(url_for('main.forum'))

        # ✅ 根据可见性决定 allowed_users
        if visibility == 'public':
            # 可设为全部用户（或仅限朋友，如果不想所有注册用户都可见）
            allowed_users = User.query.all()
        else:
            allowed_ids = request.form.getlist('allowed_users')  # 多选框
            allowed_users = User.query.filter(User.id.in_(allowed_ids)).all()

        # ✅ 创建 GameEntry 并附加 allowed_users
        new_entry = GameEntry(
            game_title=game_title,
            date_played=date_played,
            user_id=current_user.id,
            allowed_users=allowed_users
        )
        db.session.add(new_entry)
        db.session.commit()

        flash('Entry submitted!')
        return redirect(url_for('main.forum'))

    # ✅ GET 请求：只显示“自己上传的”和“被授权查看”的记录
    page = request.args.get('page', 1, type=int)
    all_entries = GameEntry.query.order_by(GameEntry.timestamp.desc()).all()

    visible_entries = [
        entry for entry in all_entries
        if entry.user_id == current_user.id or current_user in entry.allowed_users
    ]

    # ✅ 手动分页
    per_page = 5
    total = len(visible_entries)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_items = visible_entries[start:end]

    class ManualPagination:
        def __init__(self, items, page, per_page, total):
            self.items = items
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = (total + per_page - 1) // per_page
            self.has_prev = page > 1
            self.has_next = page < self.pages
            self.prev_num = page - 1
            self.next_num = page + 1

    pagination = ManualPagination(paginated_items, page, per_page, total)

    entries = []
    for entry in paginated_items:
        entries.append({
            'entry': entry,
            'like_count': entry.likes.count(),
            'favorite_count': entry.favorites.count(),
            'liked': Like.query.filter_by(user_id=current_user.id, entry_id=entry.id).first() is not None,
            'favorited': Favorite.query.filter_by(user_id=current_user.id, entry_id=entry.id).first() is not None,
        })

    friends = current_user.friends.all()

    return render_template(
        'upload-data-view.html',
        entries=entries,
        pagination=pagination,
        friends=friends
    )


@main.route('/forum/<int:entry_id>', methods=['GET', 'POST'])
@login_required
def view_entry(entry_id):
    entry = GameEntry.query.get_or_404(entry_id)

    # ✅ 权限校验：非本人 & 不在允许列表，禁止查看
    if entry.user_id != current_user.id and current_user not in entry.allowed_users:
        abort(403)

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


@main.route('/edit_bio', methods=['POST'])
@login_required
def edit_bio():
    new_bio = request.form.get('bio', '').strip()
    current_user.bio = new_bio
    db.session.commit()
    flash("Signature updated.")
    return redirect(url_for('main.profile', user_id=current_user.id))

#添加好友
# routes.py

@main.route('/send_request/<int:user_id>', methods=['POST'])
@login_required
def send_request(user_id):
    receiver = User.query.get_or_404(user_id)
    if receiver == current_user or receiver in current_user.friends:
        flash("Invalid friend request.")
        return redirect(url_for('main.profile', user_id=user_id))

    existing = FriendRequest.query.filter_by(sender_id=current_user.id, receiver_id=user_id).first()
    if existing:
        flash("Friend request already sent.")
    else:
        request = FriendRequest(sender_id=current_user.id, receiver_id=user_id)
        db.session.add(request)
        db.session.commit()
        flash("Friend request sent.")
    return redirect(url_for('main.profile', user_id=user_id))

@main.route('/friend_requests')
@login_required
def friend_requests():
    requests = FriendRequest.query.filter_by(receiver_id=current_user.id).all()
    return render_template('friend_requests.html', requests=requests)


@main.route('/accept_request/<int:request_id>', methods=['POST'])
@login_required
def accept_request(request_id):
    req = FriendRequest.query.get_or_404(request_id)
    if req.receiver_id != current_user.id:
        abort(403)

    sender = req.sender
    receiver = req.receiver

    if sender not in receiver.friends:
        receiver.friends.append(sender)
    if receiver not in sender.friends:
        sender.friends.append(receiver)

    db.session.delete(req)
    db.session.commit()

    flash(f'You are now friends with {sender.username}!', 'success')
    return redirect(url_for('main.friend_requests'))


@main.route('/decline_request/<int:request_id>', methods=['POST'])
@login_required
def decline_request(request_id):
    req = FriendRequest.query.get_or_404(request_id)
    if req.receiver_id != current_user.id:
        abort(403)

    db.session.delete(req)
    db.session.commit()
    flash('Friend request declined.', 'info')
    return redirect(url_for('main.friend_requests'))

@main.route('/chat/<int:friend_id>')
@login_required
def chat_with_friend(friend_id):
    friend = User.query.get_or_404(friend_id)
    if friend not in current_user.friends:
        flash("You can only chat with your friends.")
        return redirect(url_for('main.profile', user_id=friend_id))

    # 提取历史消息（双方互发的消息）
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == friend_id)) |
        ((Message.sender_id == friend_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.timestamp.asc()).all()

    history = [{
        "from": msg.sender.username,
        "message": msg.content,
        "timestamp": msg.timestamp.strftime('%H:%M')
    } for msg in messages]

    return render_template("chat.html", users=current_user.friends, history=history)


#找回密码
@main.route('/reset_request', methods=['GET', 'POST'])
def reset_request():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            send_reset_email(user)
            flash("Reset email sent!", "info")
        else:
            flash("Email not found.", "danger")
        return redirect(url_for('main.login'))  # 登录页
    return render_template('forgotpassword.html')  # 你已有的模板


@main.route('/reset/<token>', methods=['GET', 'POST'])
def reset_token(token):
    email = verify_reset_token(token)
    if email is None:
        flash('Invalid or expired token.', 'danger')
        return redirect(url_for('main.reset_request'))

    user = User.query.filter_by(email=email).first_or_404()

    if request.method == 'POST':
        password = request.form.get('password')
        user.set_password(password)
        db.session.commit()
        flash("Your password has been updated.", "success")
        return redirect(url_for('main.login'))

    # ✅ 传入 user 变量！
    return render_template('reset_password.html', user=user,token=token)



def generate_reset_token(email, expires_sec=3600):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return s.dumps(email, salt='reset-password')

def verify_reset_token(token):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        return s.loads(token, salt='reset-password', max_age=3600)
    except Exception:
        return None

def send_reset_email(user):
    token = generate_reset_token(user.email)
    reset_url = url_for('main.reset_token', token=token, _external=True)
    msg = MailMessage('Reset Your Password',
                  recipients=[user.email])
    msg.body = f'''Hi {user.username},

To reset your password, click the link below:
{reset_url}

If you did not request this, please ignore this email.

Thanks,
Board Game Central
'''
    mail.send(msg)