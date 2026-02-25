from app import create_app
from app.models import Student
app = create_app()
with app.app_context():
    s = Student.query.first()
    if s:
        print(s.id)
    else:
        print("None")
