from flask import Blueprint, render_template, request, redirect, url_for, flash, g, abort
from app.models import Setting, User, Session
from app.utils import login_required, require_role
from app.extensions import db

bp = Blueprint('settings', __name__, url_prefix='/settings')

@bp.route("/", methods=["GET", "POST"])
@login_required
@require_role("admin", "principal", "vice_principal")
def index():
    if request.method == "POST":
        if g.user.role not in ["admin", "principal"]:
            abort(403)
        # Update school name
        school_name = request.form.get("school_name")
        if school_name:
            s = Setting.query.filter_by(school_id=g.school.id, key="school_name").first()
            if not s:
                s = Setting(school_id=g.school.id, key="school_name")
            s.value = school_name
            db.session.add(s)
            db.session.commit()
            flash("Settings updated.", "s")
        return redirect(url_for("settings.index"))

    settings = {s.key: s.value for s in Setting.query.filter_by(school_id=g.school.id).all()}
    teachers = User.query.filter_by(school_id=g.school.id, role='teacher').all()
    sessions = Session.query.filter_by(school_id=g.school.id).order_by(Session.id.desc()).all()

    return render_template("settings/index.html", settings=settings, teachers=teachers, sessions=sessions)

@bp.route("/logs")
@login_required
@require_role("admin", "principal")
def view_logs():
    from app.models import AuditLog
    logs = AuditLog.query.filter_by(school_id=g.school.id).order_by(AuditLog.timestamp.desc()).limit(100).all()
    return render_template("settings/logs.html", logs=logs)

@bp.route("/add-teacher", methods=["POST"])
@login_required
@require_role("admin", "principal")
def add_teacher():
    username = request.form.get("username")
    password = request.form.get("password")
    if username and password:
        if User.query.filter_by(school_id=g.school.id, username=username).first():
            flash("Username already exists in this school.", "danger")
        else:
            new_teacher = User(school_id=g.school.id, username=username, role='teacher')
            new_teacher.set_password(password)
            db.session.add(new_teacher)
            db.session.commit()
            flash("Teacher added.", "s")
    return redirect(url_for("settings.index"))

@bp.route("/add-session", methods=["POST"])
@login_required
@require_role("admin", "principal")
def add_session():
    name = request.form.get("name")
    if name:
        # Create new session
        new_sess = Session(school_id=g.school.id, name=name, is_current=False)
        db.session.add(new_sess)
        db.session.commit()
        flash(f"Session {name} created.", "s")
    return redirect(url_for("settings.index"))

@bp.route("/set-current-session/<int:session_id>")
@login_required
@require_role("admin", "principal")
def set_current_session(session_id):
    sess = Session.query.filter_by(id=session_id, school_id=g.school.id).first_or_404()
    # Unset all
    Session.query.filter_by(school_id=g.school.id).update({Session.is_current: False})
    # Set this one
    sess.is_current = True
    db.session.commit()
    flash(f"Current session set to {sess.name}.", "s")
    return redirect(url_for("settings.index"))
