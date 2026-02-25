from flask import Blueprint, render_template, request, g, redirect, url_for, flash
from app.models import Class, Student, Exam
from app.utils import login_required
from app.extensions import db

bp = Blueprint('main', __name__)

@bp.route("/")
@login_required
def home():
    if g.user.role == 'student':
        return redirect(url_for('student_portal.dashboard'))

    class_count = Class.query.filter_by(school_id=g.school.id, session_id=g.current_session.id).count()
    student_count = Student.query.filter_by(school_id=g.school.id).count()
    exam_count = Exam.query.filter_by(school_id=g.school.id).count()

    return render_template("main/home.html",
                           class_count=class_count,
                           student_count=student_count,
                           exam_count=exam_count)

@bp.route("/search")
@login_required
def search():
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
