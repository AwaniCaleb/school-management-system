from flask import Blueprint, render_template, request, redirect, url_for, flash, g, abort
from app.models import Class, Student
from app.utils import login_required, require_role
from app.extensions import db

bp = Blueprint('students', __name__)

@bp.route("/students")
@login_required
def directory():
    students = Student.query.filter_by(school_id=g.school.id).order_by(Student.name).all()
    return render_template("students/directory.html", students=students)

@bp.route("/student/<int:student_id>")
@login_required
def profile(student_id):
    stu = Student.query.filter_by(id=student_id, school_id=g.school.id).first_or_404()
    return render_template("students/profile.html", stu=stu)

@bp.route("/add-student", methods=["GET", "POST"])
@login_required
def enroll_student():
    if request.method == "POST":
        new_student = Student(
            school_id=g.school.id,
            name=request.form["name"].strip(),
            gender=request.form.get("gender"),
            dob=request.form.get("dob"),
            blood_group=request.form.get("blood_group"),
            religion=request.form.get("religion"),
            state_of_origin=request.form.get("state_of_origin"),
            guardian_name=request.form.get("guardian_name"),
            guardian_phone=request.form.get("guardian_phone"),
            contact_no=request.form.get("contact_no"),
            address=request.form.get("address"),
            medical_notes=request.form.get("medical_notes")
        )
        db.session.add(new_student)
        db.session.commit()
        flash("Student enrolled in system!", "s")
        return redirect(url_for("students.directory"))
    return render_template("students/add.html", cls=None)

@bp.route("/add-to-class/<int:class_id>", methods=["GET", "POST"])
@login_required
def add_to_class(class_id):
    cls = Class.query.filter_by(id=class_id, school_id=g.school.id).first_or_404()
    if request.method == "POST":
        student_id = request.form.get("student_id")
        roll_no = request.form.get("roll_no")

        if not student_id or not roll_no:
            flash("Student and Roll Number are required.", "danger")
        else:
            stu = Student.query.filter_by(id=student_id, school_id=g.school.id).first_or_404()
            existing = Student.query.filter_by(school_id=g.school.id, class_id=class_id, roll_no=roll_no).first()
            if existing:
                flash(f"Roll number {roll_no} already exists in this class!", "danger")
            else:
                stu.class_id = class_id
                stu.roll_no = roll_no
                db.session.commit()
                flash(f"{stu.name} added to {cls.class_name}!", "s")
                return redirect(url_for("classes.class_detail", class_id=class_id))

    available_students = Student.query.filter(
        Student.school_id == g.school.id,
        ((Student.class_id == None) | (Student.class_id != class_id))
    ).all()
    return render_template("students/add_to_class.html", cls=cls, available_students=available_students)

@bp.route("/student/<int:student_id>/edit", methods=["GET", "POST"])
@login_required
def edit_student(student_id):
    stu = Student.query.filter_by(id=student_id, school_id=g.school.id).first_or_404()
    if request.method == "POST":
        stu.name = request.form["name"].strip()
        stu.roll_no = request.form.get("roll_no")
        stu.gender = request.form.get("gender")
        stu.dob = request.form.get("dob")
        stu.blood_group = request.form.get("blood_group")
        stu.religion = request.form.get("religion")
        stu.state_of_origin = request.form.get("state_of_origin")
        stu.guardian_name = request.form.get("guardian_name")
        stu.guardian_phone = request.form.get("guardian_phone")
        stu.contact_no = request.form.get("contact_no")
        stu.address = request.form.get("address")
        stu.medical_notes = request.form.get("medical_notes")
        try:
            db.session.commit()
            flash("Student updated.", "s")
            return redirect(url_for("students.profile", student_id=stu.id))
        except:
            db.session.rollback()
            flash("Could not update student. Check if roll number is duplicated.", "danger")

    return render_template("students/edit.html", stu=stu)

@bp.route("/student/<int:student_id>/delete", methods=["POST"])
@login_required
@require_role("admin", "principal")
def delete_student(student_id):
    stu = Student.query.filter_by(id=student_id, school_id=g.school.id).first_or_404()
    db.session.delete(stu)
    db.session.commit()
    flash("Student record removed from system.", "s")
    return redirect(url_for("students.directory"))
