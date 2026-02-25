from flask import Blueprint, render_template, g, redirect, url_for, flash
from app.models import Student, Exam, Mark, FeeStructure, FeePayment
from app.utils import login_required
from app.extensions import db

bp = Blueprint('student_portal', __name__, url_prefix='/student_portal')

@bp.route("/")
@login_required
def dashboard():
    if g.user.role != 'student' or not g.user.student_id:
        flash("Access restricted to student accounts.", "danger")
        return redirect(url_for('main.home'))

    stu = Student.query.get(g.user.student_id)
    if not stu:
        flash("Student profile not found.", "danger")
        return redirect(url_for('auth.logout'))

    # Get results for latest exam
    latest_exam = None
    results = []
    total = 0
    max_total = 0
    percentage = 0

    if stu.student_class:
        latest_exam = Exam.query.filter_by(class_id=stu.class_id).order_by(Exam.id.desc()).first()
        if latest_exam:
            for sub in stu.student_class.subjects:
                mark = Mark.query.filter_by(student_id=stu.id, subject_id=sub.id, exam_id=latest_exam.id).first()
                val = mark.marks_obtained if mark else 0.0
                results.append({'subject_name': sub.subject_name, 'marks': val})
                total += val
            max_total = len(results) * 100
            percentage = (total / max_total * 100) if max_total else 0.0

    # Fee status
    total_due = sum(f.amount for f in stu.student_class.fee_structures) if stu.student_class else 0
    total_paid = sum(p.paid_amount for p in stu.fee_payments)
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

    stu = Student.query.get(g.user.student_id)
    exams = Exam.query.filter_by(class_id=stu.class_id).all() if stu.class_id else []

    return render_template("student_portal/results.html", stu=stu, exams=exams)
