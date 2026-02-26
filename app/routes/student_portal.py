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

    if stu.student_class:
        latest_exam = Exam.query.filter_by(
            class_id=stu.class_id,
            school_id=g.school.id,
            session_id=g.current_session.id
        ).order_by(Exam.id.desc()).first()

        if latest_exam:
            # For results, we should probably look at subjects assigned to this class in THIS session
            from app.models import SubjectTeacherAssignment, Subject
            assignments = SubjectTeacherAssignment.query.filter_by(
                class_id=stu.class_id,
                session_id=g.current_session.id
            ).all()

            for assign in assignments:
                sub = assign.subject
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
    # Get all exams the student has marks in, along with their session info
    results_list = db.session.query(Exam).join(Mark).filter(Mark.student_id == stu.id).distinct().order_by(Exam.session_id.desc(), Exam.id.desc()).all()

    return render_template("student_portal/results.html", stu=stu, exams=results_list)

@bp.route("/profile")
@login_required
def profile():
    if g.user.role != 'student' or not g.user.student_id:
        return redirect(url_for('main.home'))

    stu = Student.query.filter_by(id=g.user.student_id, school_id=g.school.id).first_or_404()
    return render_template("student_portal/profile.html", stu=stu)

@bp.route("/report-card/<int:exam_id>")
@login_required
def report_card(exam_id):
    if g.user.role != 'student' or not g.user.student_id:
        return redirect(url_for('main.home'))

    stu = Student.query.filter_by(id=g.user.student_id, school_id=g.school.id).first_or_404()
    exam = Exam.query.filter_by(id=exam_id, class_id=stu.class_id).first_or_404()

    results = []
    total = 0
    from app.models import SubjectTeacherAssignment, Mark
    assignments = SubjectTeacherAssignment.query.filter_by(class_id=stu.class_id, session_id=exam.session_id).all()
    for a in assignments:
        sub = a.subject
        mark = Mark.query.filter_by(student_id=stu.id, subject_id=sub.id, exam_id=exam.id).first()
        val = mark.marks_obtained if mark else 0.0
        results.append({
            'subject_name': sub.subject_name,
            'marks': val,
            'verification_code': mark.verification_code if mark else 'N/A'
        })
        total += val

    max_total = len(results) * 100
    percentage = (total / max_total * 100) if max_total else 0.0

    return render_template("exams/result.html", stu=stu, exam=exam, results=results, total=total, max_total=max_total, percentage=percentage)

@bp.route("/subjects")
@login_required
def subjects():
    if g.user.role != 'student' or not g.user.student_id:
        return redirect(url_for('main.home'))

    stu = Student.query.filter_by(id=g.user.student_id, school_id=g.school.id).first()
    if not stu.class_id:
        flash("You are not currently assigned to a class.", "info")
        return redirect(url_for('.dashboard'))

    from app.models import SubjectTeacherAssignment
    # Get subjects assigned to this class for the current session
    assignments = SubjectTeacherAssignment.query.filter_by(
        class_id=stu.class_id,
        session_id=g.current_session.id
    ).all()

    return render_template("student_portal/subjects.html", stu=stu, assignments=assignments)

@bp.route("/payments")
@login_required
def payments():
    if g.user.role != 'student' or not g.user.student_id:
        return redirect(url_for('main.home'))

    stu = Student.query.filter_by(id=g.user.student_id, school_id=g.school.id).first()

    # Fees for current session
    fee_structures = FeeStructure.query.filter_by(
        class_id=stu.class_id,
        session_id=g.current_session.id
    ).all()

    # Detailed payment history
    history = FeePayment.query.filter_by(student_id=stu.id).order_by(FeePayment.paid_on.desc()).all()

    # Calculate summary per fee structure
    summary = []
    total_due = 0
    total_paid = 0

    for fs in fee_structures:
        paid_for_this = db.session.query(db.func.sum(FeePayment.paid_amount)).filter_by(
            student_id=stu.id,
            fee_id=fs.id
        ).scalar() or 0

        summary.append({
            'name': fs.name,
            'amount': fs.amount,
            'paid': paid_for_this,
            'balance': fs.amount - paid_for_this,
            'due_date': fs.due_date
        })
        total_due += fs.amount
        total_paid += paid_for_this

    return render_template("student_portal/payments.html",
                           stu=stu,
                           summary=summary,
                           history=history,
                           total_due=total_due,
                           total_paid=total_paid,
                           total_balance=total_due - total_paid)
