from app import create_app
from app.extensions import db
from app.models import School, Session, User, Class, Subject, Student, Exam, FeeStructure, Setting, Mark, AttendanceSession, AttendanceRecord, FeePayment, SubjectTeacherAssignment
from werkzeug.security import generate_password_hash
from datetime import date, timedelta
import random
import warnings
from sqlalchemy.exc import SAWarning

def seed_db():
    warnings.filterwarnings("ignore", category=SAWarning, message="Can't sort tables for DROP")
    app = create_app()
    with app.app_context():
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
        s1_sess_cur = Session(name='2024/2025', is_current=True, school_id=school1.id)
        db.session.add(s1_sess_cur)
        db.session.flush()

        # Administrative Roles for School 1
        s1_admin = User(username='admin', role='admin', school_id=school1.id)
        s1_admin.set_password('admin123')
        s1_principal = User(username='principal', role='principal', school_id=school1.id)
        s1_principal.set_password('principal123')
        s1_vp = User(username='vp_academic', role='vice_principal', school_id=school1.id)
        s1_vp.set_password('vp123')
        db.session.add_all([s1_admin, s1_principal, s1_vp])

        # Teachers for School 1
        teacher_data = [
            ('adeyemi_f', 'Mr. Femi Adeyemi'),
            ('balogun_b', 'Mrs. Bisi Balogun'),
            ('okonkwo_c', 'Mr. Chinedu Okonkwo'),
            ('chioma_n', 'Ms. Ngozi Chioma')
        ]
        s1_teachers = []
        for uname, name in teacher_data:
            t = User(username=uname, role='teacher', school_id=school1.id)
            t.set_password('teacher123')
            db.session.add(t)
            s1_teachers.append(t)
        db.session.flush()

        # Classes (Exist across all sessions)
        class_names = ['JSS 1', 'JSS 2', 'JSS 3', 'SS 1', 'SS 2', 'SS 3']
        db_classes = []
        for name in class_names:
            for sec in ['A', 'B']:
                c = Class(
                    school_id=school1.id,
                    class_name=name,
                    section=sec,
                    form_teacher_id=random.choice(s1_teachers).id
                )
                db.session.add(c)
                db_classes.append(c)
        db.session.flush()

        # Subjects (Exist across all sessions)
        nigerian_subjects = ['Mathematics', 'English Language', 'Biology', 'Civic Education', 'Economics', 'Physics', 'Chemistry']
        db_subjects = []
        for s_name in nigerian_subjects:
            sub = Subject(subject_name=s_name, school_id=school1.id)
            db.session.add(sub)
            db_subjects.append(sub)
        db.session.flush()

        # Subject Assignments for CURRENT Session
        for c in db_classes:
            selected_subs = random.sample(db_subjects, 5)
            for sub in selected_subs:
                assign = SubjectTeacherAssignment(
                    session_id=s1_sess_cur.id,
                    class_id=c.id,
                    subject_id=sub.id,
                    teacher_id=random.choice(s1_teachers).id
                )
                db.session.add(assign)

        # Students and Student Portal Logins
        first_names_m = ['Olumide', 'Emeka', 'Tunde', 'Abubakar', 'Chinedu']
        first_names_f = ['Chioma', 'Adesua', 'Fatima', 'Ngozi', 'Zainab']
        last_names = ['Okonkwo', 'Adeyemi', 'Balogun', 'Bello', 'Eze']

        for c in db_classes:
            for i in range(1, 4): # 3 students per class
                gender = random.choice(['Male', 'Female'])
                f_name = random.choice(first_names_m if gender == 'Male' else first_names_f)
                l_name = random.choice(last_names)
                stu = Student(
                    school_id=school1.id,
                    class_id=c.id,
                    name=f"{f_name} {l_name}",
                    roll_no=f"{c.class_name.replace(' ', '')}{c.section}0{i}",
                    gender=gender,
                    dob='2011-04-10',
                    guardian_name=f"Mr. {l_name}",
                    status='Active'
                )
                db.session.add(stu)
                db.session.flush()

                # Student Login Credentials
                stu_user = User(
                    school_id=school1.id,
                    username=stu.roll_no.lower(), # Username is the roll number
                    role='student',
                    student_id=stu.id
                )
                stu_user.set_password('student123')
                db.session.add(stu_user)

        # Exams for Current Session
        jss1a = Class.query.filter_by(school_id=school1.id, class_name='JSS 1', section='A').first()
        exam = Exam(
            school_id=school1.id,
            session_id=s1_sess_cur.id,
            class_id=jss1a.id,
            name='First Term Examination',
            exam_type='Final',
            weight=1.0
        )
        db.session.add(exam)
        db.session.flush()

        # Settings
        settings = [
            Setting(school_id=school1.id, key='school_name', value=school1.name),
            Setting(school_id=school1.id, key='grade_a', value='70'),
            Setting(school_id=school1.id, key='grade_b', value='60'),
            Setting(school_id=school1.id, key='grade_c', value='50'),
            Setting(school_id=school1.id, key='grade_d', value='40'),
        ]
        db.session.add_all(settings)

        # Marks
        for stu in jss1a.students:
            # Only subjects assigned to this class in this session
            assignments = SubjectTeacherAssignment.query.filter_by(class_id=jss1a.id, session_id=s1_sess_cur.id).all()
            for a in assignments:
                mark = Mark(
                    student_id=stu.id,
                    subject_id=a.subject_id,
                    exam_id=exam.id,
                    marks_obtained=random.randint(50, 95)
                )
                db.session.add(mark)

        db.session.commit()
        print("SaaS Hierarchical Database Seeded!")
        print("-" * 30)
        print(f"SCHOOL: {school1.name}")
        print(f"ADMIN: admin / admin123")
        print(f"PRINCIPAL: principal / principal123")
        print(f"TEACHER: {s1_teachers[0].username} / teacher123")
        print(f"STUDENT: {jss1a.students[0].roll_no.lower()} / student123")
        print("-" * 30)

if __name__ == "__main__":
    seed_db()
