from flask import Blueprint, jsonify, request, g
from app.models import Student, Mark, Exam, Class, Subject
from app.extensions import db
from app.utils import login_required

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/stats')
@login_required
def get_stats():
    return jsonify({
        'classes': Class.query.filter_by(school_id=g.school.id, session_id=g.current_session.id).count(),
        'students': Student.query.filter_by(school_id=g.school.id).count(),
        'exams': Exam.query.filter_by(school_id=g.school.id).join(Class).filter(Class.session_id == g.current_session.id).count()
    })

@bp.route('/class/<int:class_id>/performance')
@login_required
def class_performance(class_id):
    # Get average marks per exam for this class
    exams = Exam.query.filter_by(class_id=class_id, school_id=g.school.id).all()
    data = []
    for e in exams:
        avg = db.session.query(db.func.avg(Mark.marks_obtained)).filter_by(exam_id=e.id).scalar() or 0
        data.append({'exam': e.name, 'average': round(avg, 2)})
    return jsonify(data)

@bp.route('/overall-performance')
@login_required
def overall_performance():
    # Average marks per class for current session
    classes = Class.query.filter_by(school_id=g.school.id, session_id=g.current_session.id).all()
    data = []
    for c in classes:
        avg = db.session.query(db.func.avg(Mark.marks_obtained)).join(Subject).filter(Subject.class_id == c.id).scalar() or 0
        data.append({'class': f"{c.class_name}-{c.section}", 'average': round(avg, 2)})
    return jsonify(data)
