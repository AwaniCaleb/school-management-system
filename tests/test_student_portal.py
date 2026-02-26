import pytest
from app.models import Student, User, School, Session, Class, Subject, SubjectTeacherAssignment, FeeStructure, FeePayment
from app.extensions import db

def setup_student_data(app):
    with app.app_context():
        # Clear existing data to avoid conflicts between tests
        db.session.query(SubjectTeacherAssignment).delete()
        db.session.query(FeeStructure).delete()
        db.session.query(Student).delete()
        db.session.query(User).delete()
        db.session.query(Class).delete()
        db.session.query(Subject).delete()

        school = School.query.first()
        session = Session.query.filter_by(is_current=True).first()

        # Create Class
        cls = Class(class_name='JSS 1', section='A', school_id=school.id)
        db.session.add(cls)
        db.session.commit()

        # Create Student
        student = Student(name='Test Student', roll_no='ST001', class_id=cls.id, school_id=school.id)
        db.session.add(student)
        db.session.commit()

        # Create User for Student
        user = User(username='ST001', role='student', student_id=student.id, school_id=school.id)
        user.set_password('pass123')
        db.session.add(user)

        # Create Teacher
        teacher_user = User(username='teacher1', role='teacher', full_name='Teacher One', email='t1@test.com', school_id=school.id)
        teacher_user.set_password('pass123')
        db.session.add(teacher_user)
        db.session.commit()

        # Create Subject and Assignment
        sub = Subject(subject_name='Math', school_id=school.id)
        db.session.add(sub)
        db.session.commit()

        assign = SubjectTeacherAssignment(session_id=session.id, class_id=cls.id, subject_id=sub.id, teacher_id=teacher_user.id)
        db.session.add(assign)

        # Create Fee
        fee = FeeStructure(class_id=cls.id, name='Tuition', amount=1000.0, due_date='2024-12-31', school_id=school.id, session_id=session.id)
        db.session.add(fee)
        db.session.commit()

        return user

def test_student_dashboard_access(client, app):
    setup_student_data(app)
    client.post('/login', data={'username': 'ST001', 'password': 'pass123'}, follow_redirects=True)
    response = client.get('/student-portal/')
    assert response.status_code == 200
    assert b'My Dashboard' in response.data

def test_student_subjects_access(client, app):
    setup_student_data(app)
    client.post('/login', data={'username': 'ST001', 'password': 'pass123'}, follow_redirects=True)
    response = client.get('/student-portal/subjects')
    assert response.status_code == 200
    assert b'My Subjects' in response.data
    assert b'Teacher One' in response.data

def test_student_payments_access(client, app):
    setup_student_data(app)
    client.post('/login', data={'username': 'ST001', 'password': 'pass123'}, follow_redirects=True)
    response = client.get('/student-portal/payments')
    assert response.status_code == 200
    assert b'Financial Overview' in response.data
    assert b'Tuition' in response.data
