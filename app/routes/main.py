from flask import Blueprint, render_template, request, g, redirect, url_for, flash
from app.models import Class, Student, Exam
from app.utils import login_required
from app.extensions import db

bp = Blueprint('main', __name__)

@bp.route("/")
@login_required
def home():
    class_count = Class.query.count()
    student_count = Student.query.count()
    exam_count = Exam.query.count()
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
        (Student.name.like(like)) | (Student.roll_no.like(like))
    ).all()

    return render_template("main/search_results.html", results=results, query=q)

@bp.route("/howto")
def howto():
    return render_template('howto.html')
