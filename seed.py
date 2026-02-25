from app import create_app
from app.extensions import db
from app.models import User, Class, Subject, Student, Exam, FeeStructure, Setting, Mark, AttendanceSession, AttendanceRecord, FeePayment
from werkzeug.security import generate_password_hash
from datetime import date, timedelta
import random

def seed_db():
    app = create_app()
    with app.app_context():
        # Drop all and create all for a fresh start
        db.drop_all()
        db.create_all()

        # 1. Add Administrative Hierarchy
        users = [
            User(username='admin', role='admin'),
            User(username='principal', role='principal'),
            User(username='vice_principal', role='vice_principal')
        ]
        for u in users:
            u.set_password('admin123')
            db.session.add(u)

        # 2. Add Teachers
        teacher_names = ['Mr. Adeyemi', 'Mrs. Balogun', 'Mr. Okonkwo', 'Ms. Chioma', 'Mr. Ibrahim', 'Mrs. Gbadamosi']
        teachers = []
        for i, name in enumerate(teacher_names):
            username = name.lower().replace('.', '').replace(' ', '_')
            t = User(username=username, role='teacher')
            t.set_password('teacher123')
            db.session.add(t)
            teachers.append(t)

        # Add default settings
        db.session.add(Setting(key='school_name', value='Lagos Heritage International School'))

        # 3. Add Nigerian Classes and Form Teachers
        class_names = ['JSS 1', 'JSS 2', 'JSS 3', 'SS 1', 'SS 2', 'SS 3']
        sections = ['A', 'B']
        db_classes = []
        teacher_idx = 0
        for name in class_names:
            for sec in sections:
                c = Class(
                    class_name=name,
                    section=sec,
                    form_teacher_id=teachers[teacher_idx % len(teachers)].id
                )
                db.session.add(c)
                db_classes.append(c)
                teacher_idx += 1

        db.session.commit()

        # 4. Nigerian Subjects and Subject Teachers
        nigerian_subjects = ['Mathematics', 'English Language', 'Civic Education', 'Biology', 'Economics', 'Government', 'Physics', 'Chemistry', 'Agricultural Science', 'Literature-in-English']

        for c in db_classes:
            selected_subs = random.sample(nigerian_subjects, 6)
            for s_name in selected_subs:
                # Assign a random teacher to each subject
                sub = Subject(
                    subject_name=s_name,
                    class_id=c.id,
                    teacher_id=random.choice(teachers).id
                )
                db.session.add(sub)

        db.session.commit()

        # 5. Nigerian Students and Student Logins
        first_names_m = ['Olumide', 'Emeka', 'Tunde', 'Abubakar', 'Chinedu', 'Adebayo', 'Femi', 'Musa', 'Ibrahim', 'Oche']
        first_names_f = ['Chioma', 'Adesua', 'Fatima', 'Ngozi', 'Zainab', 'Funke', 'Ifunanya', 'Bisi', 'Oluwaseun', 'Amaka']
        last_names = ['Okonkwo', 'Adeyemi', 'Balogun', 'Bello', 'Eze', 'Danladi', 'Ojo', 'Nwosu', 'Gbadamosi', 'Okafor']
        states = ['Lagos', 'Oyo', 'Kano', 'Enugu', 'Rivers', 'Kaduna', 'Abuja FCT', 'Ogun', 'Edo', 'Delta']
        religions = ['Christianity', 'Islam', 'Other']
        blood_groups = ['A+', 'B+', 'O+', 'AB+', 'O-']

        for c in db_classes:
            for i in range(10, 14): # 4 students per class for brevity
                gender = random.choice(['Male', 'Female'])
                f_name = random.choice(first_names_m if gender == 'Male' else first_names_f)
                l_name = random.choice(last_names)
                s = Student(
                    name=f"{f_name} {l_name}",
                    roll_no=f"{c.class_name.replace(' ', '')}{c.section}{i}",
                    class_id=c.id,
                    gender=gender,
                    dob=(date.today() - timedelta(days=random.randint(4000, 6000))).isoformat(),
                    blood_group=random.choice(blood_groups),
                    religion=random.choice(religions),
                    state_of_origin=random.choice(states),
                    guardian_name=f"{random.choice(last_names)} {random.choice(first_names_m)}",
                    guardian_phone=f"080{random.randint(10000000, 99999999)}",
                    contact_no=f"081{random.randint(10000000, 99999999)}",
                    address=f"{random.randint(1, 100)} Herbert Macaulay Way, Yaba, Lagos",
                    medical_notes=random.choice(['None', 'Allergic to Peanuts', 'Asthmatic', 'None'])
                )
                db.session.add(s)
                db.session.flush() # To get student.id

                # Create student user account
                stu_user = User(
                    username=s.roll_no.lower(),
                    role='student',
                    student_id=s.id
                )
                stu_user.set_password('student123')
                db.session.add(stu_user)

        db.session.commit()

        # 6. Exams and Marks for JSS 1A
        jss1a = Class.query.filter_by(class_name='JSS 1', section='A').first()
        exam = Exam(name='First Term Examination', exam_type='Theory', weight=1.0, class_id=jss1a.id)
        db.session.add(exam)
        db.session.commit()

        for s in jss1a.students:
            for sub in jss1a.subjects:
                mark = Mark(
                    student_id=s.id,
                    subject_id=sub.id,
                    exam_id=exam.id,
                    marks_obtained=random.randint(45, 98)
                )
                db.session.add(mark)

        # 7. Attendance and Fees
        for c in db_classes:
            # Create a session for today
            sess = AttendanceSession(class_id=c.id, date=date.today().isoformat())
            db.session.add(sess)
            db.session.commit()
            for s in c.students:
                rec = AttendanceRecord(session_id=sess.id, student_id=s.id, status='P')
                db.session.add(rec)

            # Fees
            f1 = FeeStructure(name='Tuition Fee', amount=50000.0, due_date='2025-09-01', class_id=c.id)
            db.session.add(f1)
            db.session.commit()

            # Record some payments
            for s in c.students[:2]:
                pay = FeePayment(
                    student_id=s.id,
                    fee_id=f1.id,
                    paid_amount=50000.0,
                    paid_on=date.today().isoformat(),
                    mode='Direct Deposit'
                )
                db.session.add(pay)

        db.session.commit()
        print("Professional Role-Based Database Seeded Successfully!")

if __name__ == "__main__":
    seed_db()
