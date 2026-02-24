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
