from app import create_app
from app.extensions import db
from app.models import School, Session, User, Class, Subject, Student, Exam, FeeStructure, Setting, Mark, AttendanceSession, AttendanceRecord, FeePayment
from werkzeug.security import generate_password_hash
from datetime import date, timedelta
import random
import warnings
from sqlalchemy.exc import SAWarning

def seed_db():
    warnings.filterwarnings("ignore", category=SAWarning, message="Can't sort tables for DROP")
    app = create_app()
    with app.app_context():
        # Drop all and create all for a fresh start
        db.session.execute(db.text("PRAGMA foreign_keys = OFF;"))
        db.drop_all()
        db.create_all()
        db.session.execute(db.text("PRAGMA foreign_keys = ON;"))

        # --- TENANT 1: LAGOS HERITAGE ---
        school1 = School(
            name='Lagos Heritage International School',
            subdomain='lagos-heritage',
            address='123 Herbert Macaulay Way, Yaba, Lagos',
            contact_email='admin@lagosheritage.edu.ng'
        )
        db.session.add(school1)
        db.session.flush()

        # Sessions for School 1
        s1_sess_old = Session(name='2023/2024', is_current=False, school_id=school1.id)
        s1_sess_cur = Session(name='2024/2025', is_current=True, school_id=school1.id)
        db.session.add_all([s1_sess_old, s1_sess_cur])
        db.session.flush()

        # Users for School 1
        s1_admin = User(username='admin', role='admin', school_id=school1.id)
        s1_admin.set_password('admin123')
        s1_principal = User(username='principal', role='principal', school_id=school1.id)
        s1_principal.set_password('admin123')
        db.session.add_all([s1_admin, s1_principal])

        # Teachers for School 1
        s1_teachers = []
        for name in ['Mr. Adeyemi', 'Mrs. Balogun', 'Mr. Okonkwo']:
            t = User(username=name.lower().replace(' ', '_').replace('.', ''), role='teacher', school_id=school1.id)
            t.set_password('teacher123')
            db.session.add(t)
            s1_teachers.append(t)
        db.session.flush()

        # Settings for School 1
        db.session.add(Setting(school_id=school1.id, key='school_name', value=school1.name))

        # --- TENANT 2: ABUJA ACADEMY ---
        school2 = School(
            name='Abuja Academy of Excellence',
            subdomain='abuja-academy',
            address='Maitama District, Abuja FCT',
            contact_email='info@abujaacademy.edu.ng'
        )
        db.session.add(school2)
        db.session.flush()

        s2_sess_cur = Session(name='2024/2025', is_current=True, school_id=school2.id)
        db.session.add(s2_sess_cur)
        db.session.flush()

        s2_admin = User(username='admin', role='admin', school_id=school2.id)
        s2_admin.set_password('admin123')
        db.session.add(s2_admin)
        db.session.add(Setting(school_id=school2.id, key='school_name', value=school2.name))

        # --- DATA GENERATION HELPER ---
        first_names_m = ['Olumide', 'Emeka', 'Tunde', 'Abubakar', 'Chinedu', 'Adebayo', 'Femi', 'Musa', 'Ibrahim', 'Oche']
        first_names_f = ['Chioma', 'Adesua', 'Fatima', 'Ngozi', 'Zainab', 'Funke', 'Ifunanya', 'Bisi', 'Oluwaseun', 'Amaka']
        last_names = ['Okonkwo', 'Adeyemi', 'Balogun', 'Bello', 'Eze', 'Danladi', 'Ojo', 'Nwosu', 'Gbadamosi', 'Okafor']
        subjects_list = ['Mathematics', 'English Language', 'Biology', 'Civic Education', 'Economics']

        # Populate School 1
        class_names = ['JSS 1', 'JSS 2', 'JSS 3', 'SS 1', 'SS 2', 'SS 3']
        for c_name in class_names:
            for sec in ['A', 'B']:
                c = Class(
                    school_id=school1.id,
                    session_id=s1_sess_cur.id,
                    class_name=c_name,
                    section=sec,
                    form_teacher_id=random.choice(s1_teachers).id
                )
                db.session.add(c)
                db.session.flush()

                # Add subjects
                for sub_name in subjects_list:
                    sub = Subject(
                        school_id=school1.id,
                        class_id=c.id,
                        subject_name=sub_name,
                        teacher_id=random.choice(s1_teachers).id
                    )
                    db.session.add(sub)

                # Add students
                for i in range(1, 5):
                    gender = random.choice(['Male', 'Female'])
                    f_name = random.choice(first_names_m if gender == 'Male' else first_names_f)
                    l_name = random.choice(last_names)
                    stu = Student(
                        school_id=school1.id,
                        class_id=c.id,
                        name=f"{f_name} {l_name}",
                        roll_no=f"{c.class_name.replace(' ', '')}{c.section}0{i}",
                        gender=gender,
                        dob='2010-05-15',
                        guardian_name=f"Mr. {l_name}",
                        status='Active'
                    )
                    db.session.add(stu)
                    db.session.flush()

                    # Student User
                    stu_user = User(
                        school_id=school1.id,
                        username=stu.roll_no.lower(),
                        role='student',
                        student_id=stu.id
                    )
                    stu_user.set_password('student123')
                    db.session.add(stu_user)

                # Add an Exam for this class
                exam = Exam(
                    school_id=school1.id,
                    class_id=c.id,
                    name='First Term Exam',
                    exam_type='Final',
                    weight=1.0
                )
                db.session.add(exam)

        db.session.commit()
        print("SaaS Role-Based Nigerian Database Seeded Successfully!")
        print(f"School 1: {school1.name} (Subdomain: {school1.subdomain})")
        print(f"School 2: {school2.name} (Subdomain: {school2.subdomain})")
        print("Default Login: admin / admin123")

if __name__ == "__main__":
    seed_db()
