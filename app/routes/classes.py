from flask import Blueprint, render_template, request, redirect, url_for, flash, g, abort
from app.models import Class, Student, Subject, Exam, User
from app.utils import login_required, require_role, can_manage_class
from app.extensions import db

bp = Blueprint('classes', __name__)

@bp.route("/classes")
@login_required
def list_classes():
    if g.user.role == 'teacher':
        # Show classes where they are form teacher OR teach a subject
        classes = Class.query.filter(
            (Class.form_teacher_id == g.user.id) |
            (Class.subjects.any(Subject.teacher_id == g.user.id))
        ).order_by(Class.class_name, Class.section).all()
    elif g.user.role == 'student':
        # Students only see their own class if assigned
        if g.user.student_id:
            from app.models import Student
            stu = Student.query.get(g.user.student_id)
            classes = [stu.student_class] if stu.student_class else []
        else:
            classes = []
    else:
        # Admin, Principal, Vice Principal see all
        classes = Class.query.order_by(Class.class_name, Class.section).all()

    return render_template("classes/list.html", classes=classes)

@bp.route("/add_class", methods=["GET", "POST"])
@login_required
@require_role("admin")
def add_class():
    if request.method == "POST":
        name = request.form["class_name"].strip()
        section = request.form["section"].strip().upper()
        if not name or not section:
            flash("Class name and section are required.", "danger")
        else:
            existing = Class.query.filter_by(class_name=name, section=section).first()
            if existing:
                flash("Class with this name and section already exists!", "danger")
            else:
                new_class = Class(class_name=name, section=section)
                db.session.add(new_class)
                db.session.commit()
                flash(f"Class {name}-{section} added!", "s")
                return redirect(url_for("classes.list_classes"))

    return render_template("classes/add.html")

@bp.route("/class/<int:class_id>")
@login_required
def class_detail(class_id):
    cls = Class.query.get_or_404(class_id)
    if not can_manage_class(cls) and not any(s.teacher_id == g.user.id for s in cls.subjects):
        if g.user.role != 'student' or (g.user.student_id and Student.query.get(g.user.student_id).class_id != class_id):
            abort(403)

    return render_template("classes/detail.html", cls=cls)

@bp.route("/class/<int:class_id>/edit", methods=["GET", "POST"])
@login_required
@require_role("admin", "principal")
def edit_class(class_id):
    cls = Class.query.get_or_404(class_id)
    teachers = User.query.filter_by(role='teacher').all()

    if request.method == "POST":
        cls.class_name = request.form["class_name"].strip()
        cls.section = request.form["section"].strip().upper()
        form_teacher_id = request.form.get("form_teacher_id")
        cls.form_teacher_id = int(form_teacher_id) if form_teacher_id else None

        try:
            db.session.commit()
            flash("Class updated successfully!", "s")
            return redirect(url_for("classes.class_detail", class_id=cls.id))
        except:
            db.session.rollback()
            flash("Another class with same name & section already exists!", "danger")

    return render_template("classes/edit.html", cls=cls, teachers=teachers)

@bp.route("/class/<int:class_id>/delete", methods=["POST"])
@login_required
@require_role("admin")
def delete_class(class_id):
    cls = Class.query.get_or_404(class_id)
    db.session.delete(cls)
    db.session.commit()
    flash("Class and all related data deleted.", "s")
    return redirect(url_for("classes.list_classes"))

@bp.route("/promote/<int:class_id>", methods=["GET", "POST"])
@login_required
@require_role("admin")
def promote_class(class_id):
    source = Class.query.get_or_404(class_id)
    target_classes = Class.query.filter(Class.id != class_id).all()

    if request.method == "POST":
        target_id = request.form.get("target_class")
        move = request.form.get("move") == "on"
        if not target_id:
            flash("Select a target class.", "danger")
        else:
            target_class = Class.query.get(target_id)
            for stu in source.students:
                # Check if student already in target
                existing = Student.query.filter_by(class_id=target_id, roll_no=stu.roll_no).first()
                if not existing:
                    new_stu = Student(name=stu.name, roll_no=stu.roll_no, class_id=target_id)
                    db.session.add(new_stu)

            if move:
                for stu in list(source.students):
                    db.session.delete(stu)

            db.session.commit()
            flash("Promotion completed.", "s")
            return redirect(url_for("classes.class_detail", class_id=target_id))

    return render_template("classes/promote.html", source=source, target_classes=target_classes)

@bp.route("/add_subject/<int:class_id>", methods=["GET", "POST"])
@login_required
@require_role("admin")
def add_subject(class_id):
    cls = Class.query.get_or_404(class_id)
    if request.method == "POST":
        sub_name = request.form["subject"].strip()
        if not sub_name:
            flash("Subject name is required.", "danger")
        else:
            new_sub = Subject(subject_name=sub_name, class_id=class_id)
            db.session.add(new_sub)
            db.session.commit()
            flash("Subject added!", "s")
            return redirect(url_for("classes.class_detail", class_id=class_id))

    return render_template("subjects/add.html", cls=cls)

@bp.route("/subject/<int:subject_id>/edit", methods=["GET", "POST"])
@login_required
@require_role("admin", "principal")
def edit_subject(subject_id):
    sub = Subject.query.get_or_404(subject_id)
    teachers = User.query.filter_by(role='teacher').all()

    if request.method == "POST":
        sub.subject_name = request.form["subject"].strip()
        teacher_id = request.form.get("teacher_id")
        sub.teacher_id = int(teacher_id) if teacher_id else None
        db.session.commit()
        flash("Subject updated!", "s")
        return redirect(url_for("classes.class_detail", class_id=sub.class_id))

    return render_template("subjects/edit.html", sub=sub, teachers=teachers)

@bp.route("/subject/<int:subject_id>/delete", methods=["POST"])
@login_required
@require_role("admin")
def delete_subject(subject_id):
    sub = Subject.query.get_or_404(subject_id)
    class_id = sub.class_id
    db.session.delete(sub)
    db.session.commit()
    flash("Subject and all related marks deleted.", "s")
    return redirect(url_for("classes.class_detail", class_id=class_id))

@bp.route("/class/<int:class_id>/students/csv")
@login_required
def export_students_csv(class_id):
    import io
    import csv
    from flask import Response
    cls = Class.query.get_or_404(class_id)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Roll No", "Name", "Gender", "DOB", "Guardian", "Contact", "Address"])

    for s in cls.students:
        writer.writerow([s.roll_no, s.name, s.gender, s.dob, s.guardian_name, s.contact_no, s.address])

    output.seek(0)
    filename = f"students_{cls.class_name}_{cls.section}.csv"
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )
