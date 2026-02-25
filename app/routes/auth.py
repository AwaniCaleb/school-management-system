from flask import Blueprint, request, redirect, render_template, url_for, flash, session, g
from app.models import User, Setting, School, Session
from app.extensions import db

bp = Blueprint('auth', __name__)

@bp.before_app_request
def load_logged_in_user():
    # Identify School
    # In production, this would use request.host to match subdomain
    host = request.host.split(':')[0]
    subdomain = host.split('.')[0]

    # Try matching subdomain
    school = School.query.filter_by(subdomain=subdomain).first()

    # Fallback for development/demo: if no subdomain match, use the first school
    if not school:
        school = School.query.first()

    g.school = school

    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        # Authenticate user within the context of the school
        if g.school:
            g.user = User.query.filter_by(id=user_id, school_id=g.school.id).first()
        else:
            g.user = None

        if not g.user and user_id:
            session.clear()

    if g.school:
        # Load current academic session
        g.current_session = Session.query.filter_by(school_id=g.school.id, is_current=True).first()
        if not g.current_session:
            g.current_session = Session.query.filter_by(school_id=g.school.id).order_by(Session.id.desc()).first()

        # Load settings
        g.settings = {s.key: s.value for s in Setting.query.filter_by(school_id=g.school.id).all()}
    else:
        g.current_session = None
        g.settings = {}

@bp.route("/login", methods=["GET", "POST"])
def login():
    if not g.school:
        return "No school configured in system. Please run seeder.", 500

    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        # Check user in the current school context
        user = User.query.filter_by(username=username, school_id=g.school.id).first()

        if user is None or not user.check_password(password):
            flash("Invalid username or password.", "danger")
        else:
            session.clear()
            session["user_id"] = user.id
            from app.utils import log_action
            log_action(f"User {username} logged in")
            flash("Logged in successfully.", "s")

            if user.role == 'student':
                return redirect(url_for('student_portal.dashboard'))
            return redirect(url_for('main.home'))

    return render_template("auth/login.html")

@bp.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "s")
    return redirect(url_for("auth.login"))
