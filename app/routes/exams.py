from flask import Blueprint, render_template, request, redirect, url_for, flash, g, abort, Response, send_file
from app.models import Class, Student, Subject, Exam, Mark, SubjectTeacherAssignment
from app.utils import login_required, require_role, is_subject_teacher, can_manage_class
from app.extensions import db
import io
import csv

bp = Blueprint('exams', __name__)

@bp.route("/exams/<int:class_id>", methods=["GET", "POST"])
@login_required
@require_role("admin", "principal", "vp_academic", "vp_admin", "hod", "teacher")
def list_exams(class_id):
    cls = Class.query.filter_by(id=class_id, school_id=g.school.id).first_or_404()
    if request.method == "POST":
        name = request.form["name"].strip()
        exam_type = request.form["exam_type"].strip()
        try:
            weight = float(request.form.get("weight", "1"))
        except ValueError:
            weight = 1.0

        if not name:
            flash("Exam name is required.", "danger")
        else:
            new_exam = Exam(
                name=name,
                exam_type=exam_type,
                weight=weight,
                class_id=class_id,
                school_id=g.school.id,
                session_id=g.current_session.id
            )
            db.session.add(new_exam)
            db.session.commit()
            flash("Exam added.", "s")
            return redirect(url_for("exams.list_exams", class_id=class_id))

    return render_template("exams/list.html", cls=cls)

@bp.route("/enter-marks/<int:class_id>", methods=["GET", "POST"])
@login_required
@require_role("admin", "principal", "vp_academic", "hod", "teacher")
def enter_marks(class_id):
    exam_id = request.args.get("exam_id") or request.form.get("exam_id")
    if not exam_id:
        flash("Exam not selected.", "danger")
        return redirect(url_for("exams.list_exams", class_id=class_id))

    cls = Class.query.filter_by(id=class_id, school_id=g.school.id).first_or_404()
    exam = Exam.query.filter_by(id=exam_id, class_id=class_id, school_id=g.school.id).first_or_404()

    assignments = SubjectTeacherAssignment.query.filter_by(class_id=class_id, session_id=exam.session_id).all()

    if request.method == "POST":
        for s in cls.students:
            for a in assignments:
                sub = a.subject
                if not is_subject_teacher(a):
                    continue

                field_name = f"marks_{s.id}_{sub.id}"
                marks_str = request.form.get(field_name, "0")
                try:
                    val = float(marks_str)
                except ValueError:
                    val = 0.0

                mark = Mark.query.filter_by(student_id=s.id, subject_id=sub.id, exam_id=exam.id).first()
                if mark:
                    mark.marks_obtained = val
                else:
                    mark = Mark(student_id=s.id, subject_id=sub.id, exam_id=exam.id, marks_obtained=val)
                    db.session.add(mark)

        db.session.commit()
        flash("All marks saved successfully!", "s")
        return redirect(url_for("exams.enter_marks", class_id=class_id, exam_id=exam_id))

    marks_map = {(m.student_id, m.subject_id): m.marks_obtained for m in exam.marks}

    return render_template("exams/enter_marks.html",
                           cls=cls,
                           exam=exam,
                           marks_map=marks_map,
                           assignments=assignments,
                           is_subject_teacher=is_subject_teacher)

@bp.route("/result/<int:student_id>")
@login_required
@require_role("admin", "principal", "vp_academic", "vp_admin", "hod", "teacher")
def student_result(student_id):
    stu = Student.query.filter_by(id=student_id, school_id=g.school.id).first_or_404()
    exam_id = request.args.get("exam_id")

    if not exam_id:
        latest_exam = Exam.query.filter_by(
            class_id=stu.class_id,
            school_id=g.school.id,
            session_id=g.current_session.id
        ).order_by(Exam.id.desc()).first()
        if not latest_exam:
            flash("No exams for this class.", "danger")
            return redirect(url_for("classes.class_detail", class_id=stu.class_id))
        exam_id = latest_exam.id

    exam = Exam.query.filter_by(id=exam_id, class_id=stu.class_id).first_or_404()
    results = []
    total = 0
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

@bp.route("/class/<int:class_id>/results")
@login_required
@require_role("admin", "principal", "vp_academic", "vp_admin", "hod", "teacher")
def class_results(class_id):
    cls = Class.query.filter_by(id=class_id, school_id=g.school.id).first_or_404()
    exam_id = request.args.get("exam_id")

    if not exam_id:
        latest_exam = Exam.query.filter_by(
            class_id=class_id,
            school_id=g.school.id,
            session_id=g.current_session.id
        ).order_by(Exam.id.desc()).first()
        if not latest_exam:
            flash("No exams defined for this class.", "danger")
            return redirect(url_for("classes.class_detail", class_id=class_id))
        exam_id = latest_exam.id

    exam = Exam.query.filter_by(id=exam_id, class_id=class_id).first_or_404()
    subject_count = SubjectTeacherAssignment.query.filter_by(class_id=class_id, session_id=exam.session_id).count()

    student_results = []
    for s in cls.students:
        total = db.session.query(db.func.sum(Mark.marks_obtained)).filter_by(student_id=s.id, exam_id=exam.id).scalar() or 0.0
        student_results.append({'student': s, 'total': total})

    student_results.sort(key=lambda x: x['total'], reverse=True)

    return render_template("exams/class_results.html", cls=cls, exam=exam, student_results=student_results, subject_count=subject_count)
