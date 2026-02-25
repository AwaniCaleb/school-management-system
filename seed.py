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

        # Add Admin
        admin = User(username='admin', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)

        # Add Teacher
        teacher = User(username='teacher', role='teacher')
        teacher.set_password('teacher123')
        db.session.add(teacher)

        # Add default settings
        db.session.add(Setting(key='school_name', value='Lagos Heritage International School'))

        # Add Nigerian Classes
        class_names = ['JSS 1', 'JSS 2', 'JSS 3', 'SS 1', 'SS 2', 'SS 3']
        sections = ['A', 'B']
        db_classes = []
        for name in class_names:
            for sec in sections:
                c = Class(class_name=name, section=sec)
                db.session.add(c)
                db_classes.append(c)

        db.session.commit()

        # Nigerian Subjects
        nigerian_subjects = ['Mathematics', 'English Language', 'Civic Education', 'Biology', 'Economics', 'Government', 'Physics', 'Chemistry', 'Agricultural Science', 'Literature-in-English']

        for c in db_classes:
            selected_subs = random.sample(nigerian_subjects, 6)
            for s_name in selected_subs:
                sub = Subject(subject_name=s_name, class_id=c.id)
                db.session.add(sub)

        db.session.commit()

        # Nigerian Names and Data
        first_names_m = ['Olumide', 'Emeka', 'Tunde', 'Abubakar', 'Chinedu', 'Adebayo', 'Femi', 'Musa', 'Ibrahim', 'Oche']
        first_names_f = ['Chioma', 'Adesua', 'Fatima', 'Ngozi', 'Zainab', 'Funke', 'Ifunanya', 'Bisi', 'Oluwaseun', 'Amaka']
        last_names = ['Okonkwo', 'Adeyemi', 'Balogun', 'Bello', 'Eze', 'Danladi', 'Ojo', 'Nwosu', 'Gbadamosi', 'Okafor']
        states = ['Lagos', 'Oyo', 'Kano', 'Enugu', 'Rivers', 'Kaduna', 'Abuja FCT', 'Ogun', 'Edo', 'Delta']
        religions = ['Christianity', 'Islam', 'Other']
        blood_groups = ['A+', 'B+', 'O+', 'AB+', 'O-']

        # Add Students
        for c in db_classes:
            for i in range(10, 16): # 6 students per class
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
                    medical_notes=random.choice(['None', 'Allergic to Peanuts', 'Asthmatic', 'None', 'None'])
                )
                db.session.add(s)

        # Add some unassigned students
        for i in range(5):
            gender = random.choice(['Male', 'Female'])
            f_name = random.choice(first_names_m if gender == 'Male' else first_names_f)
            l_name = random.choice(last_names)
            s = Student(
                name=f"{f_name} {l_name}",
                gender=gender,
                dob=(date.today() - timedelta(days=random.randint(4000, 6000))).isoformat(),
                blood_group=random.choice(blood_groups),
                religion=random.choice(religions),
                state_of_origin=random.choice(states),
                status='Active'
            )
            db.session.add(s)

        db.session.commit()

        # Add Exams and Marks for JSS 1A
        jss1a = Class.query.filter_by(class_name='JSS 1', section='A').first()
        exams = [
            Exam(name='First Term Mid-Term', exam_type='Theory', weight=0.3, class_id=jss1a.id),
            Exam(name='First Term Examination', exam_type='Theory', weight=0.7, class_id=jss1a.id)
        ]
        db_exams = []
        for ex in exams:
            db.session.add(ex)
            db_exams.append(ex)
        db.session.commit()

        for e in db_exams:
            for s in jss1a.students:
                for sub in jss1a.subjects:
                    mark = Mark(
                        student_id=s.id,
                        subject_id=sub.id,
                        exam_id=e.id,
                        marks_obtained=random.randint(40, 95)
                    )
                    db.session.add(mark)

        # Add Attendance for JSS 1A
        for i in range(5):
            d = date.today() - timedelta(days=i)
            session_row = AttendanceSession(class_id=jss1a.id, date=d.isoformat())
            db.session.add(session_row)
            db.session.commit()
            for s in jss1a.students:
                record = AttendanceRecord(
                    session_id=session_row.id,
                    student_id=s.id,
                    status=random.choice(['P', 'P', 'P', 'A'])
                )
                db.session.add(record)

        # Add Fees for all classes
        for c in db_classes:
            f1 = FeeStructure(name='Tuition Fee', amount=45000.0, due_date='2025-05-15', class_id=c.id)
            f2 = FeeStructure(name='Development Levy', amount=15000.0, due_date='2025-05-15', class_id=c.id)
            db.session.add_all([f1, f2])
            db.session.commit()

            for s in c.students[:3]:
                pay = FeePayment(
                    student_id=s.id,
                    fee_id=f1.id,
                    paid_amount=random.choice([10000, 25000, 45000]),
                    paid_on=date.today().isoformat(),
                    mode='Bank Transfer'
                )
                db.session.add(pay)

        db.session.commit()
        print("Database initialized and seeded with comprehensive Nigerian data successfully!")

if __name__ == "__main__":
    seed_db()
