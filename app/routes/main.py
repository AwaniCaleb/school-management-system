from flask import Blueprint, render_template, request, g, redirect, url_for, flash, abort
from app.models import Class, Student, Exam
from app.utils import login_required
from app.extensions import db

bp = Blueprint('main', __name__)

@bp.route("/")
@login_required
def home():
    if g.user.role == 'student':
        return redirect(url_for('student_portal.dashboard'))

    from app.models import SubjectTeacherAssignment
    if g.user.role == 'teacher':
        # Stats for this teacher
        assigned_classes = Class.query.filter(
            Class.school_id == g.school.id,
            ((Class.form_teacher_id == g.user.id) |
             (Class.subject_assignments.any(
                 (SubjectTeacherAssignment.teacher_id == g.user.id) &
                 (SubjectTeacherAssignment.session_id == g.current_session.id)
             )))
        ).distinct().all()

        class_count = len(assigned_classes)
        # Total unique students this teacher interacts with
        student_ids = set()
        for cls in assigned_classes:
            for s in cls.students:
                student_ids.add(s.id)
        student_count = len(student_ids)

        # Exams for these classes in current session
        assigned_class_ids = [c.id for c in assigned_classes]
        exam_count = Exam.query.filter(
            Exam.class_id.in_(assigned_class_ids),
            Exam.session_id == g.current_session.id
        ).count()
    else:
        # Admin/Principal see global stats for current session where applicable
        class_count = Class.query.filter_by(school_id=g.school.id).count()
        student_count = Student.query.filter_by(school_id=g.school.id).count()
        exam_count = Exam.query.filter_by(school_id=g.school.id, session_id=g.current_session.id).count()

    return render_template("main/home.html",
                           class_count=class_count,
                           student_count=student_count,
                           exam_count=exam_count)

@bp.route("/search")
@login_required
def search():
    if g.user.role == 'student':
        abort(403)
    q = request.args.get("q", "").strip()
    if not q:
        flash("Please enter name or roll number to search.", "danger")
        return redirect(url_for("main.home"))

    like = f"%{q}%"
    results = Student.query.filter(
        Student.school_id == g.school.id,
        (Student.name.like(like)) | (Student.roll_no.like(like))
    ).all()

    return render_template("main/search_results.html", results=results, query=q)

@bp.route("/howto")
def howto():
    return render_template('main/howto.html')
