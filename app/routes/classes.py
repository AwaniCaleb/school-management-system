from flask import Blueprint, render_template, request, redirect, url_for, flash, g, abort
from app.models import Class, Student, Subject, Exam, User, SubjectTeacherAssignment
from app.utils import login_required, require_role, can_manage_class
from app.extensions import db

bp = Blueprint('classes', __name__)

@bp.route("/classes")
@login_required
@require_role("admin", "principal", "vice_principal", "teacher")
def list_classes():
    if g.user.role == 'teacher':
        # For teachers, show classes where they are form teacher OR have a subject assignment in CURRENT session
        classes = Class.query.filter(
            Class.school_id == g.school.id,
            ((Class.form_teacher_id == g.user.id) |
             (Class.subject_assignments.any(
                 (SubjectTeacherAssignment.teacher_id == g.user.id) &
                 (SubjectTeacherAssignment.session_id == g.current_session.id)
             )))
        ).order_by(Class.class_name, Class.section).distinct().all()
    else:
        classes = Class.query.filter_by(
            school_id=g.school.id
        ).order_by(Class.class_name, Class.section).all()

    return render_template("classes/list.html", classes=classes)

@bp.route("/add-class", methods=["GET", "POST"])
@login_required
@require_role("admin", "principal")
def add_class():
    if request.method == "POST":
        name = request.form["class_name"].strip()
        section = request.form["section"].strip().upper()
        if not name or not section:
            flash("Class name and section are required.", "danger")
        else:
            existing = Class.query.filter_by(
                school_id=g.school.id,
                class_name=name,
                section=section
            ).first()
            if existing:
                flash("Class already exists in the school directory!", "danger")
            else:
                new_class = Class(
                    school_id=g.school.id,
                    class_name=name,
                    section=section
                )
                db.session.add(new_class)
                db.session.commit()
                flash(f"Class {name}-{section} added!", "s")
                return redirect(url_for("classes.list_classes"))

    return render_template("classes/add.html")

@bp.route("/class/<int:class_id>")
@login_required
@require_role("admin", "principal", "vice_principal", "teacher")
def class_detail(class_id):
    cls = Class.query.filter_by(id=class_id, school_id=g.school.id).first_or_404()

    # Check access
    is_subject_assigned = SubjectTeacherAssignment.query.filter_by(
        class_id=class_id,
        session_id=g.current_session.id,
        teacher_id=g.user.id
    ).first() is not None

    if not can_manage_class(cls) and not is_subject_assigned:
        abort(403)

    return render_template("classes/detail.html", cls=cls)

@bp.route("/class/<int:class_id>/edit", methods=["GET", "POST"])
@login_required
@require_role("admin", "principal")
def edit_class(class_id):
    cls = Class.query.filter_by(id=class_id, school_id=g.school.id).first_or_404()
    teachers = User.query.filter_by(school_id=g.school.id, role='teacher').all()

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
@require_role("admin", "principal")
def delete_class(class_id):
    cls = Class.query.filter_by(id=class_id, school_id=g.school.id).first_or_404()
    db.session.delete(cls)
    db.session.commit()
    flash("Class and all related data deleted.", "s")
    return redirect(url_for("classes.list_classes"))

@bp.route("/promote-class/<int:class_id>", methods=["GET", "POST"])
@login_required
@require_role("admin", "principal")
def promote_class(class_id):
    source = Class.query.filter_by(id=class_id, school_id=g.school.id).first_or_404()
    # Can promote to classes in next sessions ideally, but for now allow any class in school
    target_classes = Class.query.filter(Class.school_id == g.school.id, Class.id != class_id).all()

    if request.method == "POST":
        target_id = request.form.get("target_class")
        move = request.form.get("move") == "on"
        if not target_id:
            flash("Select a target class.", "danger")
        else:
            target_class = Class.query.get(target_id)
            for stu in source.students:
                # Update roll no and class for target
                existing = Student.query.filter_by(school_id=g.school.id, class_id=target_id, roll_no=stu.roll_no).first()
                if not existing:
                    # In a real system, we'd probably create a new enrollment record
                    # Here we update the student's current class
                    stu.class_id = target_id

            db.session.commit()
            flash("Promotion completed.", "s")
            return redirect(url_for("classes.class_detail", class_id=target_id))

    return render_template("classes/promote.html", source=source, target_classes=target_classes)

@bp.route("/subjects")
@login_required
@require_role("admin", "principal")
def list_subjects():
    subjects = Subject.query.filter_by(school_id=g.school.id).order_by(Subject.subject_name).all()
    return render_template("subjects/list.html", subjects=subjects)

@bp.route("/add-subject", methods=["GET", "POST"])
@login_required
@require_role("admin", "principal")
def add_subject():
    if request.method == "POST":
        sub_name = request.form["subject"].strip()
        if not sub_name:
            flash("Subject name is required.", "danger")
        else:
            new_sub = Subject(subject_name=sub_name, school_id=g.school.id)
            db.session.add(new_sub)
            db.session.commit()
            flash("Subject added to school directory!", "s")
            return redirect(url_for("classes.list_subjects"))
    return render_template("subjects/add.html", cls=None)

@bp.route("/subject/<int:subject_id>/edit", methods=["GET", "POST"])
@login_required
@require_role("admin", "principal")
def edit_subject(subject_id):
    sub = Subject.query.filter_by(id=subject_id, school_id=g.school.id).first_or_404()
    if request.method == "POST":
        sub.subject_name = request.form["subject"].strip()
        db.session.commit()
        flash("Subject updated!", "s")
        return redirect(url_for("classes.list_subjects"))
    return render_template("subjects/edit.html", sub=sub)

@bp.route("/assign-teacher/<int:class_id>", methods=["GET", "POST"])
@login_required
@require_role("admin", "principal")
def assign_teacher(class_id):
    cls = Class.query.get_or_404(class_id)
    subjects = Subject.query.filter_by(school_id=g.school.id).all()
    teachers = User.query.filter_by(school_id=g.school.id, role='teacher').all()

    if request.method == "POST":
        subject_id = request.form.get("subject_id")
        teacher_id = request.form.get("teacher_id")

        # Upsert assignment for current session
        assign = SubjectTeacherAssignment.query.filter_by(
            session_id=g.current_session.id,
            class_id=class_id,
            subject_id=subject_id
        ).first()

        if not assign:
            assign = SubjectTeacherAssignment(
                session_id=g.current_session.id,
                class_id=class_id,
                subject_id=subject_id
            )
            db.session.add(assign)

        assign.teacher_id = teacher_id if teacher_id else None
        db.session.commit()
        flash("Teacher assigned successfully!", "s")
        return redirect(url_for('classes.class_detail', class_id=class_id))

    return render_template("subjects/assign.html", cls=cls, subjects=subjects, teachers=teachers)

@bp.route("/subject/<int:subject_id>/delete", methods=["POST"])
@login_required
@require_role("admin", "principal")
def delete_subject(subject_id):
    sub = Subject.query.filter_by(id=subject_id, school_id=g.school.id).first_or_404()
    db.session.delete(sub)
    db.session.commit()
    flash("Subject and all related marks deleted.", "s")
    return redirect(url_for("classes.list_subjects"))

@bp.route("/class/<int:class_id>/students-csv")
@login_required
@require_role("admin", "principal", "vice_principal", "teacher")
def export_students_csv(class_id):
    import io
    import csv
    from flask import Response
    cls = Class.query.filter_by(id=class_id, school_id=g.school.id).first_or_404()

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
