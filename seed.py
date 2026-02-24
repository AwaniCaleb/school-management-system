from app import create_app
from app.extensions import db
from app.models import User, Class, Subject, Student, Exam, FeeStructure, Setting
from werkzeug.security import generate_password_hash

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
        db.session.add(Setting(key='school_name', value='Global Academy'))

        # Add Classes
        c1 = Class(class_name='10th', section='A')
        c2 = Class(class_name='10th', section='B')
        c3 = Class(class_name='12th', section='Sci')
        db.session.add_all([c1, c2, c3])
        db.session.commit()

        # Add Subjects for 10th A
        sub1 = Subject(subject_name='Mathematics', class_id=c1.id)
        sub2 = Subject(subject_name='Science', class_id=c1.id)
        sub3 = Subject(subject_name='English', class_id=c1.id)
        db.session.add_all([sub1, sub2, sub3])

        # Add Students for 10th A
        s1 = Student(name='Alice Johnson', roll_no='101', class_id=c1.id, gender='Female')
        s2 = Student(name='Bob Smith', roll_no='102', class_id=c1.id, gender='Male')
        db.session.add_all([s1, s2])

        # Add Exam for 10th A
        e1 = Exam(name='Mid Term', exam_type='Theory', weight=1.0, class_id=c1.id)
        db.session.add(e1)

        # Add Fee Structure for 10th A
        f1 = FeeStructure(name='Tuition Fee', amount=5000.0, due_date='2025-06-30', class_id=c1.id)
        db.session.add(f1)

        db.session.commit()
        print("Database initialized and seeded successfully!")

if __name__ == "__main__":
    seed_db()
