from flask import Blueprint, request, redirect, render_template, url_for, flash, session, g
from app.models import User, Setting
from app.extensions import db

bp = Blueprint('auth', __name__)

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)

    # Load global settings safely
    try:
        g.settings = {s.key: s.value for s in Setting.query.all()}
    except Exception:
        g.settings = {}

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        user = User.query.filter_by(username=username).first()

        if user is None or not user.check_password(password):
            flash("Invalid username or password.", "danger")
        else:
            session.clear()
            session["user_id"] = user.id
            from app.utils import log_action
            log_action(f"User {username} logged in")
            flash("Logged in successfully.", "s")
            return redirect(url_for('main.home'))

    return render_template("auth/login.html")

@bp.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "s")
    return redirect(url_for("auth.login"))
