from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='professor')  # 'admin', 'professor', 'student'
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=True)

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)

    students = db.relationship('Student', back_populates='course')

    def __repr__(self):
        return f"<Course {self.code} - {self.title}>"

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    student_number = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    year_level = db.Column(db.String(20))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=True)

    attendances = db.relationship('Attendance', back_populates='student', cascade='all, delete-orphan')
    course = db.relationship('Course', back_populates='students', uselist=False)

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"<Student {self.student_number} - {self.full_name()}>"

class Attendance(db.Model):
    __tablename__ = 'attendances'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    status = db.Column(db.String(20), nullable=False)  # Present / Absent / Late / Excused
    notes = db.Column(db.Text)

    student = db.relationship('Student', back_populates='attendances')

    def __repr__(self):
        return f"<Attendance {self.student_id} {self.date} {self.status}>"
