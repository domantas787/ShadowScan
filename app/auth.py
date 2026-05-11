
#Handles user registration, login, and logout.
import re

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from flask_bcrypt import Bcrypt

from app.db import get_db


# using a Flask Blueprint to keep auth routes separate from the main app routes
auth_bp = Blueprint("auth", __name__)

# Flask login for session cookies
login_manager = LoginManager()
login_manager.login_view = "auth.login"   # where to send unauthenticated users

# bcrypt
bcrypt = Bcrypt()


# Allowed characters for usernames letters, numbers, underscores only.
USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_]+$')


class User(UserMixin):
    """The bare minimum a Flask-Login user class needs."""
    def __init__(self, id, username):
        self.id = id
        self.username = username


@login_manager.user_loader
def load_user(user_id):
    """Flask-Login calls this every request to figure out who the current user is."""
    conn = get_db()
    row = conn.execute(
        "SELECT id, username FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    conn.close()

    if row:
        return User(row["id"], row["username"])
    return None


# REGISTER

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    # Pull form fields
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    confirm = request.form.get("confirm", "")

    # validation
    if not username or not password:
        flash("Username and password are required.", "error")
        return render_template("register.html")

    if len(username) < 3 or len(username) > 30:
        flash("Username must be between 3 and 30 characters.", "error")
        return render_template("register.html")

    if not USERNAME_PATTERN.match(username):
        flash("Username can only contain letters, numbers, and underscores.", "error")
        return render_template("register.html")

    if len(password) < 8:
        flash("Password must be at least 8 characters.", "error")
        return render_template("register.html")

    if len(password) > 128:
        # rate limit
        flash("Password cannot exceed 128 characters.", "error")
        return render_template("register.html")

    if password != confirm:
        flash("Passwords do not match.", "error")
        return render_template("register.html")

    # Check if the username is already taken
    conn = get_db()
    existing = conn.execute(
        "SELECT id FROM users WHERE username = ?", (username,)
    ).fetchone()

    if existing:
        conn.close()
        flash("Username already taken.", "error")
        return render_template("register.html")

    # Hash the password before saving
    pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    conn.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (username, pw_hash)
    )
    conn.commit()
    conn.close()

    flash("Account created! Please log in.", "success")
    return redirect(url_for("auth.login"))


# LOGIN

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    # Rate limiting
    client_ip = request.remote_addr
    if current_app.is_rate_limited(client_ip):
        flash("Too many login attempts. Please wait a minute and try again.", "error")
        return render_template("login.html")

    current_app.record_login_attempt(client_ip)

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    conn = get_db()
    row = conn.execute(
        "SELECT id, username, password_hash FROM users WHERE username = ?",
        (username,)
    ).fetchone()
    conn.close()

    if not row or not bcrypt.check_password_hash(row["password_hash"], password):
        flash("Invalid username or password.", "error")
        return render_template("login.html")

    user = User(row["id"], row["username"])
    login_user(user)

    return redirect(url_for("dashboard"))


#LOGOUT 

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))
