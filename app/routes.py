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

from sqlalchemy import func, extract, cast, Integer

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template("index.html")

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.homepage')) 

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


@main.route('/visualisation')
def visualisation():
    return render_template("visualisation-options.html")

@main.route('/forum', methods=['GET', 'POST'])
@login_required
def forum():
    if request.method == 'POST':
        # 1. 基本游戏信息
        game_title = request.form.get('gameTitle')
        date_str   = request.form.get('datePlayed')
        visibility = request.form.get('visibility')
        try:
            date_played = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid date format.", "error")
            return redirect(url_for('main.forum'))

        # 2. 权限控制
        if visibility == 'public':
            allowed_users = User.query.all()
        else:
            allowed_ids   = request.form.getlist('allowed_users')
            allowed_users = User.query.filter(User.id.in_(allowed_ids)).all()

        # 3. 拆分每个玩家
        names              = request.form.getlist('player_name')
        usernames          = request.form.getlist('player_username')
        scores             = request.form.getlist('score')
        win_checked        = request.form.getlist('win')
        went_first_checked = request.form.getlist('went_first')
        first_checked      = request.form.getlist('first_time_playing')

        for idx, name in enumerate(names):
            uname = usernames[idx].strip()
            user = User.query.filter_by(username=uname).first() if uname else None
            entry_user = user or current_user

            entry = GameEntry(
                game_title         = game_title,
                date_played        = date_played,
                user_id            = entry_user.id,
                win                = str(idx) in win_checked,
                went_first         = str(idx) in went_first_checked,
                first_time_playing = str(idx) in first_checked,
                score              = int(scores[idx]) if scores[idx] else None,
                allowed_users      = allowed_users
            )
            db.session.add(entry)
        db.session.commit()

        flash('Entry submitted!', 'success')
        return redirect(url_for('main.forum'))

    # GET: 列表 & 分页
    page        = request.args.get('page', 1, type=int)
    all_entries = GameEntry.query.order_by(GameEntry.timestamp.desc()).all()
    visible     = [
        e for e in all_entries
        if e.user_id == current_user.id or current_user in e.allowed_users
    ]

    per_page = 5
    total    = len(visible)
    start    = (page-1)*per_page
    end      = start + per_page
    items    = visible[start:end]

    class Pagination:
        def __init__(self, page, per_page, total):
            self.page, self.per_page, self.total = page, per_page, total
            self.pages = (total + per_page - 1)//per_page
            self.has_prev = page > 1
            self.has_next = page < self.pages
            self.prev_num = page - 1
            self.next_num = page + 1

    pagination = Pagination(page, per_page, total)

    entries = []
    for e in items:
        entries.append({
            'entry':              e,
            'like_count':         e.likes.count(),
            'favorite_count':     e.favorites.count(),
            'liked':              Like.query.filter_by(user_id=current_user.id, entry_id=e.id).first() is not None,
            'favorited':          Favorite.query.filter_by(user_id=current_user.id, entry_id=e.id).first() is not None,
            'win':                e.win,
            'went_first':         e.went_first,
            'first_time_playing': e.first_time_playing,
            'score':              e.score
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


# 在文件顶部，确保有这些导入：
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import func, extract, cast, Integer
from app.models import GameEntry, User
from app import db

# … 你的其它路由 …

@main.route('/analysis')
@login_required
def analysis():
    # 1) 总局数
    plays = GameEntry.query.filter_by(user_id=current_user.id).count()

    # 2) 不同游戏数
    games = (
        db.session.query(GameEntry.game_title)
        .filter_by(user_id=current_user.id)
        .distinct()
        .count()
    )

    # 3) 不同天数
    days = (
        db.session.query(GameEntry.date_played)
        .filter_by(user_id=current_user.id)
        .distinct()
        .count()
    )

    # 4) 计算 H-index
    counts = (
        db.session.query(
            GameEntry.game_title,
            func.count(GameEntry.id).label('cnt')
        )
        .filter_by(user_id=current_user.id)
        .group_by(GameEntry.game_title)
        .order_by(func.count(GameEntry.id).desc())
        .all()
    )
    h_index = 0
    for rank, (_, cnt) in enumerate(counts, start=1):
        if cnt >= rank:
            h_index = rank
        else:
            break

    # 5) 合作过的玩家（排除自己）
    co_ids = (
        db.session.query(GameEntry.user_id)
        .filter(GameEntry.user_id != current_user.id)
        .distinct()
        .all()
    )
    co_ids = [uid for (uid,) in co_ids]
    co_players = User.query.filter(User.id.in_(co_ids)).order_by(User.username).all()
    players = len(co_players)

    # —— Chart 数据 —— #

    # A) Plays Per Month
    ppm_rows = db.session.query(
        extract('year', GameEntry.date_played).label('year'),
        extract('month', GameEntry.date_played).label('month'),
        func.count(GameEntry.id).label('count')
    ).filter_by(user_id=current_user.id)\
     .group_by('year','month')\
     .order_by('year','month')\
     .all()
    plays_per_month = [
        {'year': int(r.year), 'month': int(r.month), 'count': r.count}
        for r in ppm_rows
    ]

    # B) Top 5 Most Played Games
    tg_rows = db.session.query(
        GameEntry.game_title,
        func.count(GameEntry.id).label('count')
    ).filter_by(user_id=current_user.id)\
     .group_by(GameEntry.game_title)\
     .order_by(func.count(GameEntry.id).desc())\
     .limit(5)\
     .all()
    top_games = [
        {'game': r.game_title, 'count': r.count}
        for r in tg_rows
    ]

    # C) Player Leaderboard (global top 5 by plays & wins)
    lb_rows = db.session.query(
        GameEntry.user_id,
        func.count(GameEntry.id).label('plays'),
        func.sum(cast(GameEntry.win, Integer)).label('wins')
    ).group_by(GameEntry.user_id)\
     .order_by(func.count(GameEntry.id).desc())\
     .limit(5)\
     .all()
    leaderboard = []
    for r in lb_rows:
        user = User.query.get(r.user_id)
        wins = int(r.wins or 0)
        plays_count = r.plays
        win_rate = round(wins / plays_count * 100, 1) if plays_count else 0
        leaderboard.append({
            'username': user.username,
            'plays': plays_count,
            'wins': wins,
            'win_rate': win_rate
        })

    # D) First Play Success Rate (当前用户)
    total_first = db.session.query(func.count(GameEntry.id))\
        .filter_by(user_id=current_user.id, first_time_playing=True)\
        .scalar()
    wins_first = db.session.query(func.count(GameEntry.id))\
        .filter_by(user_id=current_user.id, first_time_playing=True, win=True)\
        .scalar()
    first_play_rate = round(wins_first / total_first * 100, 1) if total_first else 0
    first_play_stats = {
        'total': total_first,
        'wins': wins_first,
        'rate': first_play_rate
    }

    return render_template(
        'analysis.html',
        plays=plays,
        games=games,
        days=days,
        h_index=h_index,
        players=players,
        co_players=co_players,
        plays_per_month=plays_per_month,
        top_games=top_games,
        leaderboard=leaderboard,
        first_play_stats=first_play_stats
    )
