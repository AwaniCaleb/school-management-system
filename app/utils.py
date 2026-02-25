from functools import wraps
from flask import g, flash, redirect, url_for, abort

def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash("Login required.", "danger")
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

def require_role(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped_view(**kwargs):
            if g.user is None:
                flash("Login required.", "danger")
                return redirect(url_for('auth.login'))
            if g.user.role not in roles:
                abort(403)
            return view(**kwargs)
        return wrapped_view
    return decorator

def log_action(action):
    from app.models import AuditLog
    from app.extensions import db
    from flask import g
    user_id = g.user.id if g.user else None
    log = AuditLog(user_id=user_id, action=action)
    db.session.add(log)
    db.session.commit()

def is_admin():
    return g.user and g.user.role in ['admin', 'principal']

def is_form_teacher(class_obj):
    if not g.user: return False
    if is_admin(): return True
    return g.user.role == 'teacher' and class_obj.form_teacher_id == g.user.id

def is_subject_teacher(subject_obj):
    if not g.user: return False
    if is_admin(): return True
    # If they are form teacher of the class, they have access to all subjects in it?
    # User said: "Form teachers... verifying the results or grades other teachers give their students"
    # So Form teacher can view, but maybe only subject teacher can edit?
    # User: "Regular teachers... can only modify the results of students for that subject only."
    if g.user.role == 'teacher' and subject_obj.teacher_id == g.user.id:
        return True
    return False

def can_manage_class(class_obj):
    return is_admin() or is_form_teacher(class_obj)
