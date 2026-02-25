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
    school_id = g.school.id if g.school else None
    if school_id:
        log = AuditLog(user_id=user_id, school_id=school_id, action=action)
        db.session.add(log)
        db.session.commit()

def is_admin():
    return g.user and g.user.role in ['admin', 'principal']

def is_form_teacher(class_obj):
    if not g.user: return False
    if is_admin(): return True
    return g.user.role == 'teacher' and class_obj.form_teacher_id == g.user.id

def is_subject_teacher(assignment_obj):
    if not g.user: return False
    if is_admin(): return True
    if g.user.role == 'teacher' and assignment_obj.teacher_id == g.user.id:
        return True
    return False

def can_manage_class(class_obj):
    return is_admin() or is_form_teacher(class_obj)

def generate_roll_no(student, class_obj):
    if not class_obj:
        return None
    # Format: ClassSection-ID (zero padded)
    # e.g. JSS1A-05
    clean_name = "".join(class_obj.class_name.split())
    clean_section = class_obj.section.strip()
    return f"{clean_name}{clean_section}-{student.id:02d}"

def calculate_grade(percentage):
    # Load thresholds from g.settings
    # Default: A>=70, B>=60, C>=50, D>=40
    try:
        a = float(g.settings.get('grade_a', 70))
        b = float(g.settings.get('grade_b', 60))
        c = float(g.settings.get('grade_c', 50))
        d = float(g.settings.get('grade_d', 40))
    except:
        a, b, c, d = 70, 60, 50, 40

    if percentage >= a: return 'A'
    if percentage >= b: return 'B'
    if percentage >= c: return 'C'
    if percentage >= d: return 'D'
    return 'F'
