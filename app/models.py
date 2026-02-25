from app.extensions import db
from datetime import datetime
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

class School(db.Model):
    __tablename__ = 'schools'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subdomain = db.Column(db.String(50), unique=True)
    logo_url = db.Column(db.String(255))
    address = db.Column(db.String(255))
    contact_email = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sessions = db.relationship('Session', backref='school', cascade="all, delete-orphan", lazy=True)
    users = db.relationship('User', backref='school', cascade="all, delete-orphan", lazy=True)
    students = db.relationship('Student', backref='school', cascade="all, delete-orphan", lazy=True)
    classes = db.relationship('Class', backref='school', cascade="all, delete-orphan", lazy=True)
    subjects = db.relationship('Subject', backref='school', cascade="all, delete-orphan", lazy=True)
    exams = db.relationship('Exam', backref='school', cascade="all, delete-orphan", lazy=True)
    fee_structures = db.relationship('FeeStructure', backref='school', cascade="all, delete-orphan", lazy=True)
    audit_logs = db.relationship('AuditLog', backref='school', cascade="all, delete-orphan", lazy=True)
    settings = db.relationship('Setting', backref='school', cascade="all, delete-orphan", lazy=True)

class Session(db.Model):
    __tablename__ = 'sessions'
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(50), nullable=False) # e.g. "2024/2025"
    is_current = db.Column(db.Boolean, default=False)
    start_date = db.Column(db.String(10))
    end_date = db.Column(db.String(10))

    exams = db.relationship('Exam', backref='session', cascade="all, delete-orphan", lazy=True)
    fee_structures = db.relationship('FeeStructure', backref='session', cascade="all, delete-orphan", lazy=True)
    attendance_sessions = db.relationship('AttendanceSession', backref='session', cascade="all, delete-orphan", lazy=True)
    subject_assignments = db.relationship('SubjectTeacherAssignment', backref='session', cascade="all, delete-orphan", lazy=True)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id', ondelete='CASCADE'), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'admin', 'principal', 'vice_principal', 'teacher', 'student'
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='SET NULL'))

    __table_args__ = (db.UniqueConstraint('school_id', 'username', name='_school_username_uc'),)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Class(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id', ondelete='CASCADE'), nullable=False)
    class_name = db.Column(db.String(50), nullable=False)
    section = db.Column(db.String(10), nullable=False)
    form_teacher_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))

    __table_args__ = (db.UniqueConstraint('school_id', 'class_name', 'section', name='_school_class_section_uc'),)

    form_teacher = db.relationship('User', foreign_keys=[form_teacher_id], backref='assigned_classes')
    students = db.relationship('Student', foreign_keys='Student.class_id', backref='student_class', lazy=True)
    exams = db.relationship('Exam', backref='exam_class', cascade="all, delete-orphan", lazy=True)
    attendance_sessions = db.relationship('AttendanceSession', backref='session_class', cascade="all, delete-orphan", lazy=True)
    subject_assignments = db.relationship('SubjectTeacherAssignment', backref='assigned_class', cascade="all, delete-orphan", lazy=True)

class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id', ondelete='CASCADE'), nullable=False)
    subject_name = db.Column(db.String(100), nullable=False)

    assignments = db.relationship('SubjectTeacherAssignment', backref='subject', cascade="all, delete-orphan", lazy=True)

class SubjectTeacherAssignment(db.Model):
    __tablename__ = 'subject_teacher_assignments'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id', ondelete='CASCADE'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))

    teacher = db.relationship('User', backref='subject_assignments')

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    roll_no = db.Column(db.String(20))
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id', ondelete='SET NULL'))

    # Expanded Information
    gender = db.Column(db.String(10))
    dob = db.Column(db.String(10))
    blood_group = db.Column(db.String(5))
    religion = db.Column(db.String(50))
    state_of_origin = db.Column(db.String(50))
    address = db.Column(db.String(255))
    guardian_name = db.Column(db.String(100))
    guardian_phone = db.Column(db.String(20))
    contact_no = db.Column(db.String(20))
    enrollment_date = db.Column(db.String(10), default=lambda: datetime.utcnow().strftime('%Y-%m-%d'))
    status = db.Column(db.String(20), default='Active') # Active, Graduated, Withdrawn
    medical_notes = db.Column(db.Text)

    marks = db.relationship('Mark', backref='student', cascade="all, delete-orphan", lazy=True)
    attendance_records = db.relationship('AttendanceRecord', backref='student', cascade="all, delete-orphan", lazy=True)
    fee_payments = db.relationship('FeePayment', backref='student', cascade="all, delete-orphan", lazy=True)

class Exam(db.Model):
    __tablename__ = 'exams'
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id', ondelete='CASCADE'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    exam_type = db.Column(db.String(50))
    weight = db.Column(db.Float, default=1.0)

    marks = db.relationship('Mark', backref='exam', cascade="all, delete-orphan", lazy=True)

class Mark(db.Model):
    __tablename__ = 'marks'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id', ondelete='CASCADE'), nullable=False)
    marks_obtained = db.Column(db.Float, default=0.0)
    verification_code = db.Column(db.String(36), default=lambda: str(uuid.uuid4()))

class AttendanceSession(db.Model):
    __tablename__ = 'attendance_sessions'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.String(10), nullable=False) # YYYY-MM-DD
    __table_args__ = (db.UniqueConstraint('class_id', 'date', name='_class_date_uc'),)

    records = db.relationship('AttendanceRecord', backref='session', cascade="all, delete-orphan", lazy=True)

class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_records'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('attendance_sessions.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String(1), nullable=False) # 'P' or 'A'
    __table_args__ = (db.UniqueConstraint('session_id', 'student_id', name='_session_student_uc'),)

class FeeStructure(db.Model):
    __tablename__ = 'fee_structures'
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id', ondelete='CASCADE'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.String(10))

    payments = db.relationship('FeePayment', backref='fee_structure', cascade="all, delete-orphan", lazy=True)

class FeePayment(db.Model):
    __tablename__ = 'fee_payments'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    fee_id = db.Column(db.Integer, db.ForeignKey('fee_structures.id', ondelete='CASCADE'), nullable=False)
    paid_amount = db.Column(db.Float, nullable=False)
    paid_on = db.Column(db.String(10), nullable=False)
    mode = db.Column(db.String(50))

class Setting(db.Model):
    __tablename__ = 'settings'
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id', ondelete='CASCADE'), primary_key=True)
    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.String(255))

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='logs')
