from app import create_app
from models import db, Student, Attendance, User, Course
from utils import hash_password
from datetime import date, timedelta

app = create_app()
with app.app_context():
    db.drop_all()
    db.create_all()
    # create courses
    c1 = Course(code='CS101', title='Intro to Computer Science')
    c2 = Course(code='EDU201', title='Foundations of Education')
    db.session.add_all([c1, c2])
    db.session.commit()
    # sample students
    s1 = Student(student_number='S2025001', first_name='Juan', last_name='Dela Cruz', year_level='1', course_id=c1.id)
    s2 = Student(student_number='S2025002', first_name='Maria', last_name='Santos', year_level='2', course_id=c2.id)
    s3 = Student(student_number='S2025003', first_name='Pedro', last_name='Reyes', year_level='3', course_id=c1.id)
    db.session.add_all([s1, s2, s3])
    db.session.commit()
    # create users
    admin = User(username='admin', password_hash=hash_password('admin123'), role='admin')
    prof = User(username='prof', password_hash=hash_password('prof123'), role='professor')
    student_user = User(username='juan', password_hash=hash_password('juan123'), role='student', student_id=s1.id)
    db.session.add_all([admin, prof, student_user])
    db.session.commit()
    # sample attendance
    today = date.today()
    db.session.add_all([
        Attendance(student_id=s1.id, date=today, status='Present', notes='On time'),
        Attendance(student_id=s2.id, date=today - timedelta(days=1), status='Late', notes='20 minutes late'),
        Attendance(student_id=s3.id, date=today - timedelta(days=2), status='Absent', notes='Sick')
    ])
    db.session.commit()
    print("Database initialized with sample data. Admin: admin/admin123 | Prof: prof/prof123 | Student: juan/juan123")
