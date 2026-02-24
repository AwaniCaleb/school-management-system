from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from app.models import Setting, User
from app.utils import login_required, require_role
from app.extensions import db

bp = Blueprint('settings', __name__, url_prefix='/settings')

@bp.route("/", methods=["GET", "POST"])
@login_required
@require_role("admin")
def index():
    if request.method == "POST":
        # Update school name
        school_name = request.form.get("school_name")
        if school_name:
            s = Setting.query.get("school_name") or Setting(key="school_name")
            s.value = school_name
            db.session.add(s)
            db.session.commit()
            flash("Settings updated.", "s")
        return redirect(url_for("settings.index"))

    settings = {s.key: s.value for s in Setting.query.all()}
    teachers = User.query.filter_by(role='teacher').all()
    return render_template("settings/index.html", settings=settings, teachers=teachers)

@bp.route("/logs")
@login_required
@require_role("admin")
def view_logs():
    from app.models import AuditLog
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(100).all()
    return render_template("settings/logs.html", logs=logs)

@bp.route("/add_teacher", methods=["POST"])
@login_required
@require_role("admin")
def add_teacher():
    username = request.form.get("username")
    password = request.form.get("password")
    if username and password:
        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "danger")
        else:
            new_teacher = User(username=username, role='teacher')
            new_teacher.set_password(password)
            db.session.add(new_teacher)
            db.session.commit()
            flash("Teacher added.", "s")
    return redirect(url_for("settings.index"))
