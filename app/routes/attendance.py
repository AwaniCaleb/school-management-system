from flask import Blueprint, render_template, request, redirect, url_for, flash, g, abort
from app.models import Class, Student, AttendanceSession, AttendanceRecord
from app.utils import login_required, can_manage_class
from app.extensions import db
from datetime import date

bp = Blueprint('attendance', __name__)

@bp.route("/attendance/<int:class_id>", methods=["GET", "POST"])
@login_required
def take_attendance(class_id):
    cls = Class.query.filter_by(id=class_id, school_id=g.school.id).first_or_404()
    if not can_manage_class(cls):
        abort(403)

    date_str = request.args.get("date") or request.form.get("date") or date.today().isoformat()

    session_row = AttendanceSession.query.filter_by(class_id=class_id, date=date_str).first()

    if request.method == "POST":
        if not session_row:
            session_row = AttendanceSession(class_id=class_id, date=date_str)
            db.session.add(session_row)
            db.session.commit()

        # Clear old records
        AttendanceRecord.query.filter_by(session_id=session_row.id).delete()

        for stu in cls.students:
            status = "P" if request.form.get(f"present_{stu.id}") == "on" else "A"
            record = AttendanceRecord(session_id=session_row.id, student_id=stu.id, status=status)
            db.session.add(record)

        db.session.commit()
        flash("Attendance saved.", "s")
        return redirect(url_for("attendance.take_attendance", class_id=class_id, date=date_str))

    records = {r.student_id: r.status for r in session_row.records} if session_row else {}

    return render_template("attendance/take.html", cls=cls, date_str=date_str, records=records)
