import csv
import io
import json
from collections import Counter
from datetime import datetime
from os import abort

from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask import jsonify, request
from flask_login import login_user, logout_user, current_user, login_required
from flask_mail import Message as MailMessage
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from sqlalchemy import func, extract, cast, Integer
from werkzeug.security import check_password_hash

from app import db, mail
from app.forms import RegistrationForm, LoginForm
from app.models import (
    FriendRequest,
    Message,
    User,
    GameEntry,
    PlayerGameEntry,
    Comment,
    Like,
    Favorite,
    RawCSVEntry,
)

main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.homepage"))

    form = RegistrationForm()

    if form.validate_on_submit():
        existing_user = User.query.filter(
            (User.username == form.username.data) | (User.email == form.email.data)
        ).first()

        if existing_user:
            flash("Username or email already exists. Please choose another.", "error")
        else:
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash("Registration successful. You can now log in.", "success")
            return redirect(url_for("main.login"))

    return render_template("createaccount.html", form=form)


@main.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash("Logged in successfully.", "success")
            return redirect(url_for("main.index"))
        else:
            flash("Invalid email or password. Please try again.", "danger")

    return render_template("login.html", form=form)


@main.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))


@main.route("/forgot-password")
def forgot_password():
    return render_template("forgotpassword.html")


@main.route("/intro")
def intro():
    return render_template("intropage.html")


@main.route("/share")
def share_data_view():
    return render_template("share-data-view.html")


@main.route("/profile/<int:user_id>")
@login_required
def profile(user_id):
    user = User.query.get_or_404(user_id)
    is_own_profile = user.id == current_user.id

    entries = (
        GameEntry.query.filter_by(user_id=user.id)
        .order_by(GameEntry.timestamp.desc())
        .all()
    )

    liked_entries = []
    favorited_entries = []
    if is_own_profile:
        liked_entries = (
            GameEntry.query.join(Like)
            .filter(Like.user_id == user.id)
            .order_by(GameEntry.timestamp.desc())
            .all()
        )
        favorited_entries = (
            GameEntry.query.join(Favorite)
            .filter(Favorite.user_id == user.id)
            .order_by(GameEntry.timestamp.desc())
            .all()
        )

    request_sent = FriendRequest.query.filter_by(
        sender_id=current_user.id, receiver_id=user.id
    ).first()
    are_friends = user in current_user.friends

    friends = user.friends.all() if is_own_profile else None

    return render_template(
        "profile.html",
        user=user,
        entries=entries,
        liked_entries=liked_entries,
        favorited_entries=favorited_entries,
        is_own_profile=is_own_profile,
        request_sent=request_sent,
        are_friends=are_friends,
        friends=friends,
    )


@main.route("/visualisation")
def visualisation():
    return render_template("visualisation-options.html")


@main.route("/forum", methods=["GET", "POST"])
@login_required
def forum():
    if request.method == "POST":
        # Retrieving form POST data
        game_title = request.form.get("gameTitle")
        date_str = request.form.get("datePlayed")
        visibility = request.form.get("visibility")

        # Error handling date entry
        try:
            date_played = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid date format.", "error")
            return redirect(url_for("main.forum"))

        # Visibility control
        if visibility == "public":
            allowed_users = []
        else:
            allowed_ids = request.form.getlist("allowed_users")
            allowed_users = User.query.filter(User.id.in_(allowed_ids)).all()

        # Enter upload data view data into game entry table
        new_entry = GameEntry(
            game_title=game_title,
            date_played=date_played,
            user_id=current_user.id,
            allowed_users=allowed_users,
        )
        db.session.add(new_entry)
        db.session.commit()

        # Enter upload data view data into RDBMS for each *player* in a game entry
        game_entry_id = new_entry.id  # same for all players

        # Retrieve lists of form field entries
        name_list = request.form.getlist("player_name")
        username_list = [current_user.username] + request.form.getlist(
            "player_username"
        )
        win_list = request.form.getlist("win")
        went_first_list = request.form.getlist("went_first")
        first_time_playing_list = request.form.getlist("first_time_playing")
        score_list = request.form.getlist("score")

        num_players = len(name_list)  # as player name is a required field

        # Player 1's (the user) game entry
        user_player_entry = PlayerGameEntry(
            game_entry_id=game_entry_id,
            user_id=current_user.id,
            name=name_list[0],
            win=True if "0" in win_list else False,
            went_first=True if "0" in went_first_list else False,
            first_time=True if "0" in first_time_playing_list else False,
            score=score_list[0],
        )
        db.session.add(user_player_entry)

        # Other players' game entries
        if num_players > 1:
            for i in range(1, num_players):
                # Get player username
                username = username_list[i]

                # Error checking: Entered Username
                if username:
                    # Query the database to find corresponding user_id
                    user_id = (
                        User.query.add_columns(User.id)
                        .filter(User.username == username)
                        .all()
                    )

                    # Error handling: Username doesn't exist
                    if (
                        not user_id
                    ):  # if list is empty (i.e. query didn't find a username match)
                        flash("Invalid Username.", "error")
                        return redirect(url_for("main.forum"))

                # Add player game data entry to database
                if username:
                    user_id_result = db.session.execute(
                        db.select(User.id).where(User.username == username)
                    ).fetchall()
                    if len(user_id_result) != 1:
                        raise ValueError(
                            f"Expected one user ID for '{username}', got {len(user_id_result)}"
                        )

                    resolved_user_id = user_id_result[0][0]
                else:
                    resolved_user_id = None
                other_player_entry = PlayerGameEntry(
                    game_entry_id=game_entry_id,
                    user_id=resolved_user_id,  # list should only contain a single user_id
                    name=name_list[i],
                    win=True if str(i) in win_list else False,
                    went_first=True if str(i) in went_first_list else False,
                    first_time=True if str(i) in first_time_playing_list else False,
                    score=score_list[i],
                )
                db.session.add(other_player_entry)

        # Commit changes to database
        db.session.commit()

        flash("Entry submitted!")
        return redirect(url_for("main.forum"))

    # Pagination
    page = request.args.get("page", 1, type=int)
    all_entries = GameEntry.query.order_by(GameEntry.timestamp.desc()).all()
    visible = [
        e
        for e in all_entries
        if e.user_id == current_user.id
        or (e.allowed_users is None or len(e.allowed_users) == 0)  # 显式判断为空
        or current_user in e.allowed_users
    ]

    per_page = 5
    total = len(visible)
    start = (page - 1) * per_page
    end = start + per_page
    items = visible[start:end]

    class Pagination:
        def __init__(self, page, per_page, total):
            self.page, self.per_page, self.total = page, per_page, total
            self.pages = (total + per_page - 1) // per_page
            self.has_prev = page > 1
            self.has_next = page < self.pages
            self.prev_num = page - 1
            self.next_num = page + 1

    pagination = Pagination(page, per_page, total)

    entries = []
    for e in items:
        # Joins game entry tables and filters for visible entries
        player_game_entry_row = (
            PlayerGameEntry.query.outerjoin(User, PlayerGameEntry.user_id == User.id)
            .join(GameEntry, PlayerGameEntry.game_entry_id == GameEntry.id)
            .filter(PlayerGameEntry.game_entry_id == e.id)
            .add_columns(
                PlayerGameEntry.id,
                PlayerGameEntry.game_entry_id,
                PlayerGameEntry.user_id,
                User.username,
                PlayerGameEntry.name,
                PlayerGameEntry.win,
                PlayerGameEntry.went_first,
                PlayerGameEntry.first_time,
                PlayerGameEntry.score,
            )
            .all()
        )
        for player_entry in player_game_entry_row:
            entries.append(
                {
                    "entry": e,
                    "p_entry": player_entry,
                    "like_count": e.likes.count(),
                    "favorite_count": e.favorites.count(),
                    "liked": Like.query.filter_by(
                        user_id=current_user.id, entry_id=e.id
                    ).first()
                    is not None,
                    "favorited": Favorite.query.filter_by(
                        user_id=current_user.id, entry_id=e.id
                    ).first()
                    is not None,
                }
            )

    friends = current_user.friends.all()

    return render_template(
        "upload-data-view.html", entries=entries, pagination=pagination, friends=friends
    )


@main.route("/forum/<int:entry_id>", methods=["GET", "POST"])
@login_required
def view_entry(entry_id):
    entry = GameEntry.query.get_or_404(entry_id)
    formatted_time = entry.timestamp.strftime(
        "%H:%M"
    )  # formatted timestamp for table caption

    # Query to find all players from the same game session
    player_entry_rows = (
        PlayerGameEntry.query.outerjoin(User, PlayerGameEntry.user_id == User.id)
        .join(GameEntry, PlayerGameEntry.game_entry_id == GameEntry.id)
        .filter(PlayerGameEntry.game_entry_id == entry_id)
        .add_columns(
            PlayerGameEntry.user_id,
            PlayerGameEntry.name,
            User.username,
            PlayerGameEntry.win,
            PlayerGameEntry.went_first,
            PlayerGameEntry.first_time,
            PlayerGameEntry.score,
        )
        .all()
    )

    # Transforming data and entering into a list of dictionaries
    player_entries = []
    for player_entry in player_entry_rows:
        player_entries.append(
            {
                "user_id": player_entry.user_id,  # for profile hyperlinks
                "name": player_entry.name,
                "username": (
                    player_entry.username if player_entry.username is not None else "-"
                ),
                "win": "Yes" if player_entry.win else "No",
                "went_first": "Yes" if player_entry.went_first else "No",
                "first_time": "Yes" if player_entry.first_time else "No",
                "score": player_entry.score if player_entry.score is not None else "-",
            }
        )

    if entry.user_id != current_user.id and current_user not in entry.allowed_users:
        abort(403)

    if request.method == "POST":
        comment_text = request.form.get("comment")
        if comment_text:
            comment = Comment(
                content=comment_text, user_id=current_user.id, entry_id=entry.id
            )
            db.session.add(comment)
            db.session.commit()
            flash("Comment posted!")

        return redirect(url_for("main.view_entry", entry_id=entry.id))

    return render_template(
        "entry_detail.html",
        entry=entry,
        player_entries=player_entries,
        formatted_time=formatted_time,
    )


@main.route("/upload_csv", methods=["POST"])
@login_required
def upload_csv():
    file = request.files["file"]
    if file and file.filename.endswith(".csv"):
        try:
            stream = io.StringIO(file.stream.read().decode("utf-8"))
        except UnicodeDecodeError:
            stream = io.StringIO(file.stream.read().decode("ISO-8859-1"))

        reader = csv.reader(stream)
        for row in reader:
            entry = RawCSVEntry(raw_data=",".join(row), user_id=current_user.id)
            db.session.add(entry)
        db.session.commit()
        flash("CSV uploaded successfully.")
    else:
        flash("Please upload a valid CSV file.")
    return redirect(url_for("main.forum"))


@main.route("/upload_json", methods=["POST"])
@login_required
def upload_json():
    file = request.files["file"]
    if file and file.filename.endswith(".json"):
        data = json.load(file.stream)
        for item in data:
            entry = GameEntry(
                game_title=item["game_title"],
                date_played=datetime.strptime(item["date_played"], "%Y-%m-%d").date(),
                user_id=current_user.id,
            )
            db.session.add(entry)
        db.session.commit()
        flash("JSON uploaded successfully.")
    return redirect(url_for("main.forum"))


@main.route("/like/<int:entry_id>", methods=["POST"])
@login_required
def like_entry(entry_id):
    entry = GameEntry.query.get_or_404(entry_id)
    existing_like = Like.query.filter_by(
        user_id=current_user.id, entry_id=entry_id
    ).first()

    liked = False
    if existing_like:
        db.session.delete(existing_like)
    else:
        new_like = Like(user_id=current_user.id, entry_id=entry_id)
        db.session.add(new_like)
        liked = True

    db.session.commit()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify(
            {"success": True, "liked": liked, "like_count": entry.likes.count()}
        )

    flash(
        "You liked this entry!" if liked else "You unliked this entry.",
        "success" if liked else "info",
    )
    return redirect(url_for("main.forum"))


@main.route("/favorite/<int:entry_id>", methods=["POST"])
@login_required
def favorite_entry(entry_id):
    entry = GameEntry.query.get_or_404(entry_id)
    existing_favorite = Favorite.query.filter_by(
        user_id=current_user.id, entry_id=entry_id
    ).first()

    favorited = False
    if existing_favorite:
        db.session.delete(existing_favorite)
    else:
        new_favorite = Favorite(user_id=current_user.id, entry_id=entry_id)
        db.session.add(new_favorite)
        favorited = True

    db.session.commit()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify(
            {
                "success": True,
                "favorited": favorited,
                "favorite_count": entry.favorites.count(),
            }
        )

    flash(
        "Added to favorites!" if favorited else "Removed from favorites.",
        "success" if favorited else "info",
    )
    return redirect(url_for("main.forum"))


@main.route("/delete_entry/<int:entry_id>", methods=["POST"])
@login_required
def delete_entry(entry_id):
    entry = GameEntry.query.get_or_404(entry_id)

    if entry.user_id != current_user.id:
        flash("You are not authorized to delete this entry.", "error")
        return redirect(url_for("main.forum"))

    db.session.delete(entry)
    db.session.commit()
    flash("Entry deleted successfully.", "success")
    return redirect(url_for("main.forum"))


@main.route("/edit_bio", methods=["POST"])
@login_required
def edit_bio():
    new_bio = request.form.get("bio", "").strip()
    current_user.bio = new_bio
    db.session.commit()
    flash("Signature updated.")
    return redirect(url_for("main.profile", user_id=current_user.id))


@main.route("/send_request/<int:user_id>", methods=["POST"])
@login_required
def send_request(user_id):
    receiver = User.query.get_or_404(user_id)
    if receiver == current_user or receiver in current_user.friends:
        flash("Invalid friend request.")
        return redirect(url_for("main.profile", user_id=user_id))

    existing = FriendRequest.query.filter_by(
        sender_id=current_user.id, receiver_id=user_id
    ).first()
    if existing:
        flash("Friend request already sent.")
    else:
        request = FriendRequest(sender_id=current_user.id, receiver_id=user_id)
        db.session.add(request)
        db.session.commit()
        flash("Friend request sent.")
    return redirect(url_for("main.profile", user_id=user_id))


@main.route("/friend_requests")
@login_required
def friend_requests():
    requests = FriendRequest.query.filter_by(receiver_id=current_user.id).all()
    return render_template("friend_requests.html", requests=requests)


@main.route("/accept_request/<int:request_id>", methods=["POST"])
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

    flash(f"You are now friends with {sender.username}!", "success")
    return redirect(url_for("main.friend_requests"))


@main.route("/decline_request/<int:request_id>", methods=["POST"])
@login_required
def decline_request(request_id):
    req = FriendRequest.query.get_or_404(request_id)
    if req.receiver_id != current_user.id:
        abort(403)

    db.session.delete(req)
    db.session.commit()
    flash("Friend request declined.", "info")
    return redirect(url_for("main.friend_requests"))


@main.route("/chat/<int:friend_id>")
@login_required
def chat_with_friend(friend_id):
    friend = User.query.get_or_404(friend_id)
    if friend not in current_user.friends:
        flash("You can only chat with your friends.")
        return redirect(url_for("main.profile", user_id=friend_id))

    # Fetch chat history
    messages = (
        Message.query.filter(
            (
                (Message.sender_id == current_user.id)
                & (Message.receiver_id == friend_id)
            )
            | (
                (Message.sender_id == friend_id)
                & (Message.receiver_id == current_user.id)
            )
        )
        .order_by(Message.timestamp.asc())
        .all()
    )

    history = [
        {
            "from": msg.sender.username,
            "message": msg.content,
            "timestamp": msg.timestamp.strftime("%H:%M"),
        }
        for msg in messages
    ]

    return render_template("chat.html", users=current_user.friends, history=history)


@main.route("/reset_request", methods=["GET", "POST"])
def reset_request():
    if request.method == "POST":
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()
        if user:
            send_reset_email(user)
            flash("Reset email sent!", "info")
        else:
            flash("Email not found.", "danger")
        return redirect(url_for("main.login"))  # 登录页
    return render_template("forgotpassword.html")  # 你已有的模板


@main.route("/reset/<token>", methods=["GET", "POST"])
def reset_token(token):
    email = verify_reset_token(token)
    if email is None:
        flash("Invalid or expired token.", "danger")
        return redirect(url_for("main.reset_request"))

    user = User.query.filter_by(email=email).first_or_404()

    if request.method == "POST":
        password = request.form.get("password")
        user.set_password(password)
        db.session.commit()
        flash("Your password has been updated.", "success")
        return redirect(url_for("main.login"))

    # 传入 user 变量！
    return render_template("reset_password.html", user=user, token=token)


def generate_reset_token(email):
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return s.dumps(email, salt="reset-password")


def verify_reset_token(token):
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        return s.loads(token, salt="reset-password", max_age=3600)
    except (BadSignature, SignatureExpired):
        return None


def send_reset_email(user):
    token = generate_reset_token(user.email)
    reset_url = url_for("main.reset_token", token=token, _external=True)
    msg = MailMessage("Reset Your Password", recipients=[user.email])
    msg.body = f"""Hi {user.username},

To reset your password, click the link below:
{reset_url}

If you did not request this, please ignore this email.

Thanks,
Board Game Central
"""
    mail.send(msg)


@main.route("/analysis", methods=["GET", "POST"])
@login_required
def analysis():
    if request.method == "POST":
        flash("New analysis view created!", "success")
        return redirect(url_for("main.analysis"))

    entries = (
        PlayerGameEntry.query.join(
            GameEntry, PlayerGameEntry.game_entry_id == GameEntry.id
        )
        .filter(
            (PlayerGameEntry.user_id == current_user.id)
            | (GameEntry.allowed_users.any(id=current_user.id))
        )
        .add_columns(
            PlayerGameEntry.user_id, GameEntry.game_title, GameEntry.date_played
        )
        .order_by(GameEntry.timestamp.desc())
        .all()
    )

    # —— Summary ——
    plays = len(entries)
    unique_games = len({e.game_title for e in entries})
    unique_days = len({e.date_played for e in entries})

    # H-index
    freqs = sorted(Counter(e.game_title for e in entries).values(), reverse=True)
    h_index = 0
    for i, cnt in enumerate(freqs, start=1):
        if cnt >= i:
            h_index = i
        else:
            break
    h_note = f"{h_index} games were played at least {h_index} times"

    # co_players
    co_ids = {e.user_id for e in entries if e.user_id != current_user.id}
    co_players = User.query.filter(User.id.in_(co_ids)).order_by(User.username).all()
    players = len(co_ids)

    # A) Monthly plays
    ppm_rows = (
        db.session.query(
            extract("year", GameEntry.date_played).label("year"),
            extract("month", GameEntry.date_played).label("month"),
            func.count(GameEntry.id).label("count"),
        )
        .join(PlayerGameEntry, GameEntry.id == PlayerGameEntry.game_entry_id)
        .filter_by(user_id=current_user.id)
        .group_by("year", "month")
        .order_by("year", "month")
        .all()
    )
    plays_per_month = [
        {"year": int(r.year), "month": int(r.month), "count": r.count} for r in ppm_rows
    ]

    # B) Top 5 games played by current user
    tg_rows = (
        db.session.query(
            GameEntry.game_title.label("game"),
            func.count(GameEntry.id).label("count"),
        )
        .filter_by(user_id=current_user.id)
        .group_by(GameEntry.game_title)
        .order_by(func.count(GameEntry.id).desc())
        .limit(5)
        .all()
    )
    top_games = [{"game": r.game, "count": r.count} for r in tg_rows]

    # C) Leaderboard
    lb_rows = (
        db.session.query(
            PlayerGameEntry.user_id,
            func.count(PlayerGameEntry.id).label("plays"),
            func.sum(cast(PlayerGameEntry.win, Integer)).label("wins"),
        )
        .group_by(PlayerGameEntry.user_id)
        .order_by(func.count(PlayerGameEntry.id).asc())
        .limit(5)
        .all()
    )
    leaderboard = []
    for r in lb_rows:
        u = User.query.get(r.user_id)
        # no username entries are ignored as there is no unique identifier for them
        if u is None:
            continue
        wins = int(r.wins or 0)
        rate = round(wins / r.plays * 100, 1) if r.plays else 0
        leaderboard.append(
            {"username": u.username, "plays": r.plays, "wins": wins, "win_rate": rate}
        )

    # D) First-time plays
    total_first = (
        db.session.query(func.count())
        .select_from(GameEntry)
        .join(PlayerGameEntry, GameEntry.id == PlayerGameEntry.game_entry_id)
        .filter_by(first_time=True, user_id=current_user.id)
        .scalar()
        or 0
    )

    wins_first = (
        db.session.query(func.count())
        .select_from(GameEntry)
        .join(PlayerGameEntry, GameEntry.id == PlayerGameEntry.game_entry_id)
        .filter_by(first_time=True, win=True, user_id=current_user.id)
        .scalar()
        or 0
    )

    first_play_stats = {
        "total": total_first,
        "wins": wins_first,
        "rate": round(wins_first / total_first * 100, 1) if total_first else 0,
    }

    return render_template(
        "analysis.html",
        plays=plays,
        games=unique_games,
        days=unique_days,
        h_index=h_index,
        h_note=h_note,
        players=players,
        co_players=co_players,
        plays_per_month=plays_per_month,
        top_games=top_games,
        leaderboard=leaderboard,
        first_play_stats=first_play_stats,
    )
