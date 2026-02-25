from flask import Blueprint, render_template, g, redirect, url_for, flash
from app.models import Student, Exam, Mark, FeeStructure, FeePayment
from app.utils import login_required
from app.extensions import db

bp = Blueprint('student_portal', __name__, url_prefix='/student-portal')

@bp.route("/")
@login_required
def dashboard():
    if g.user.role != 'student' or not g.user.student_id:
        flash("Access restricted to student accounts.", "danger")
        return redirect(url_for('main.home'))

    stu = Student.query.filter_by(id=g.user.student_id, school_id=g.school.id).first()
    if not stu:
        flash("Student profile not found.", "danger")
        return redirect(url_for('auth.logout'))

    # Get results for latest exam in current session
    latest_exam = None
    results = []
    total = 0
    max_total = 0
    percentage = 0

    if stu.student_class and stu.student_class.session_id == g.current_session.id:
        latest_exam = Exam.query.filter_by(class_id=stu.class_id, school_id=g.school.id).order_by(Exam.id.desc()).first()
        if latest_exam:
            for sub in stu.student_class.subjects:
                mark = Mark.query.filter_by(student_id=stu.id, subject_id=sub.id, exam_id=latest_exam.id).first()
                val = mark.marks_obtained if mark else 0.0
                results.append({'subject_name': sub.subject_name, 'marks': val})
                total += val
            max_total = len(results) * 100
            percentage = (total / max_total * 100) if max_total else 0.0

    # Fee status for current session
    # Sum all fee structures for the class in the current session
    total_due = FeeStructure.query.filter_by(class_id=stu.class_id, session_id=g.current_session.id).with_entities(db.func.sum(FeeStructure.amount)).scalar() or 0
    total_paid = db.session.query(db.func.sum(FeePayment.paid_amount)).join(FeeStructure).filter(
        FeePayment.student_id == stu.id,
        FeeStructure.session_id == g.current_session.id
    ).scalar() or 0
    balance = total_due - total_paid

    return render_template("student_portal/dashboard.html",
                           stu=stu,
                           exam=latest_exam,
                           results=results,
                           total=total,
                           max_total=max_total,
                           percentage=percentage,
                           balance=balance)

@bp.route("/results")
@login_required
def view_results():
    if g.user.role != 'student' or not g.user.student_id:
        return redirect(url_for('main.home'))

    stu = Student.query.filter_by(id=g.user.student_id, school_id=g.school.id).first()
    # Can see all results across all sessions? Usually yes.
    exams = Exam.query.filter(Exam.class_id == Student.class_id, Student.id == stu.id).all() # This is simplified
    # Better: get all exams the student has marks in
    exams = db.session.query(Exam).join(Mark).filter(Mark.student_id == stu.id).distinct().all()

    return render_template("student_portal/results.html", stu=stu, exams=exams)
