from flask import Blueprint, render_template, request, redirect, url_for, flash, g, abort
from app.models import Class, Student
from app.utils import login_required, require_role
from app.extensions import db

bp = Blueprint('students', __name__)

@bp.route("/add_student/<int:class_id>", methods=["GET", "POST"])
@login_required
def add_student(class_id):
    cls = Class.query.get_or_404(class_id)
    if request.method == "POST":
        name = request.form["name"].strip()
        roll = request.form["roll_no"].strip()
        if not name or not roll:
            flash("Name and roll number are required.", "danger")
        else:
            existing = Student.query.filter_by(class_id=class_id, roll_no=roll).first()
            if existing:
                flash("Roll number already exists in this class!", "danger")
            else:
                new_student = Student(
                    name=name,
                    roll_no=roll,
                    class_id=class_id,
                    gender=request.form.get("gender"),
                    dob=request.form.get("dob"),
                    guardian_name=request.form.get("guardian_name"),
                    contact_no=request.form.get("contact_no"),
                    address=request.form.get("address")
                )
                db.session.add(new_student)
                db.session.commit()
                flash("Student added!", "s")
                return redirect(url_for("classes.class_detail", class_id=class_id))

    return render_template("students/add.html", cls=cls)

@bp.route("/student/<int:student_id>/edit", methods=["GET", "POST"])
@login_required
def edit_student(student_id):
    stu = Student.query.get_or_404(student_id)
    if request.method == "POST":
        stu.name = request.form["name"].strip()
        stu.roll_no = request.form["roll_no"].strip()
        stu.gender = request.form.get("gender")
        stu.dob = request.form.get("dob")
        stu.guardian_name = request.form.get("guardian_name")
        stu.contact_no = request.form.get("contact_no")
        stu.address = request.form.get("address")
        try:
            db.session.commit()
            flash("Student updated.", "s")
            return redirect(url_for("classes.class_detail", class_id=stu.class_id))
        except:
            db.session.rollback()
            flash("Roll number already exists in this class!", "danger")

    return render_template("students/edit.html", stu=stu)

@bp.route("/student/<int:student_id>/delete", methods=["POST"])
@login_required
@require_role("admin")
def delete_student(student_id):
    stu = Student.query.get_or_404(student_id)
    class_id = stu.class_id
    db.session.delete(stu)
    db.session.commit()
    flash("Student and all marks deleted.", "s")
    return redirect(url_for("classes.class_detail", class_id=class_id))
