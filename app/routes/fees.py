from flask import Blueprint, render_template, request, redirect, url_for, flash, g, abort
from app.models import Class, Student, FeeStructure, FeePayment, Subject
from app.utils import login_required, require_role
from app.extensions import db
from datetime import date

bp = Blueprint('fees', __name__)

@bp.route("/fees")
@login_required
def dashboard():
    from app.models import SubjectTeacherAssignment
    if g.user.role == 'teacher':
        # Show classes where they are form teacher OR have a subject assignment in CURRENT session
        classes = Class.query.filter(
            Class.school_id == g.school.id,
            ((Class.form_teacher_id == g.user.id) |
             (Class.subject_assignments.any(
                 (SubjectTeacherAssignment.teacher_id == g.user.id) &
                 (SubjectTeacherAssignment.session_id == g.current_session.id)
             )))
        ).distinct().all()
    elif g.user.role == 'student':
        return redirect(url_for('student_portal.dashboard'))
    else:
        classes = Class.query.filter_by(
            school_id=g.school.id
        ).all()
    return render_template("fees/dashboard.html", classes=classes)

@bp.route("/fees/class/<int:class_id>", methods=["GET", "POST"])
@login_required
def class_fees(class_id):
    cls = Class.query.filter_by(id=class_id, school_id=g.school.id).first_or_404()
    if request.method == "POST" and g.user.role in ['admin', 'principal', 'vice_principal']:
        name = request.form["name"].strip()
        try:
            amount = float(request.form["amount"])
        except ValueError:
            amount = 0.0
        due_date = request.form["due_date"].strip()

        if not name or amount <= 0:
            flash("Valid fee name and amount required.", "danger")
        else:
            new_fee = FeeStructure(
                name=name,
                amount=amount,
                due_date=due_date or None,
                class_id=class_id,
                school_id=g.school.id,
                session_id=g.current_session.id
            )
            db.session.add(new_fee)
            db.session.commit()
            flash("Fee item added.", "s")
            return redirect(url_for("fees.class_fees", class_id=class_id))

    fee_totals = sum(f.amount for f in cls.fee_structures)
    student_summaries = []
    for s in cls.students:
        paid = db.session.query(db.func.sum(FeePayment.paid_amount)).join(FeeStructure).filter(
            FeePayment.student_id == s.id,
            FeeStructure.class_id == class_id,
            FeeStructure.session_id == g.current_session.id
        ).scalar() or 0.0
        student_summaries.append({'student': s, 'paid': paid, 'balance': fee_totals - paid})

    return render_template("fees/class_fees.html", cls=cls, fee_totals=fee_totals, student_summaries=student_summaries)

@bp.route("/fees/student/<int:student_id>", methods=["GET", "POST"])
@login_required
def student_fees(student_id):
    stu = Student.query.filter_by(id=student_id, school_id=g.school.id).first_or_404()
    if request.method == "POST":
        fee_id = int(request.form["fee_id"])
        try:
            paid_amount = float(request.form["amount"])
        except ValueError:
            paid_amount = 0.0
        mode = request.form["mode"].strip()

        if paid_amount <= 0:
            flash("Payment amount must be positive.", "danger")
        else:
            payment = FeePayment(student_id=student_id, fee_id=fee_id, paid_amount=paid_amount, paid_on=date.today().isoformat(), mode=mode or None)
            db.session.add(payment)
            db.session.commit()
            flash("Payment recorded.", "s")
            return redirect(url_for("fees.student_fees", student_id=student_id))

    total_due = sum(f.amount for f in stu.student_class.fee_structures) if stu.student_class else 0
    total_paid = sum(p.paid_amount for p in stu.fee_payments)

    return render_template("fees/student_fees.html", stu=stu, total_due=total_due, total_paid=total_paid, balance=total_due - total_paid)
