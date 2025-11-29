from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, current_user, login_required
from models import db, User, Student, Attendance, Course
from forms import LoginForm, RegisterForm, StudentForm, AttendanceForm, CourseForm
from utils import hash_password, check_password
from datetime import datetime
from functools import wraps

bp = Blueprint('main', __name__)

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('main.login'))
            if current_user.role not in roles and current_user.role != 'admin':
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('main.dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@bp.route('/')
def index():
    return render_template('index.html')

# ---------- Auth ----------
@bp.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists.', 'danger')
            return redirect(url_for('main.register'))
        u = User(username=form.username.data, password_hash=hash_password(form.password.data), role=form.role.data)
        # if registering as student, leave student_id None for professor to assign
        db.session.add(u)
        db.session.commit()
        flash('Account created. Please log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@bp.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password(user.password_hash, form.password.data):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('main.dashboard'))
        flash('Invalid credentials.', 'danger')
    return render_template('login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out.', 'info')
    return redirect(url_for('main.index'))

# ---------- Dashboard ----------
@bp.route('/dashboard')
@login_required
def dashboard():
    # student sees own attendance
    if current_user.role == 'student' and current_user.student_id:
        student = Student.query.get(current_user.student_id)
        attendances = student.attendances if student else []
        return render_template('student_dashboard.html', student=student, attendances=attendances)
    # professors/admin see overviews
    total_students = Student.query.count()
    total_attendance = Attendance.query.count()
    recent = Attendance.query.order_by(Attendance.date.desc()).limit(6).all()
    return render_template('dashboard.html', total_students=total_students, total_attendance=total_attendance, recent=recent)

# ---------- Courses CRUD ----------
@bp.route('/courses')
@login_required
@role_required('professor')
def courses():
    courses = Course.query.order_by(Course.code).all()
    return render_template('courses.html', courses=courses)

@bp.route('/courses/add', methods=['GET','POST'])
@login_required
@role_required('professor')
def add_course():
    form = CourseForm()
    if form.validate_on_submit():
        c = Course(code=form.code.data.strip(), title=form.title.data.strip())
        db.session.add(c)
        db.session.commit()
        flash('Course added.', 'success')
        return redirect(url_for('main.courses'))
    return render_template('course_form.html', form=form, action='Add')

@bp.route('/courses/<int:id>/edit', methods=['GET','POST'])
@login_required
@role_required('professor')
def edit_course(id):
    c = Course.query.get_or_404(id)
    form = CourseForm(obj=c)
    if form.validate_on_submit():
        c.code = form.code.data.strip()
        c.title = form.title.data.strip()
        db.session.commit()
        flash('Course updated.', 'success')
        return redirect(url_for('main.courses'))
    return render_template('course_form.html', form=form, action='Edit')

@bp.route('/courses/<int:id>/delete', methods=['POST'])
@login_required
@role_required('professor')
def delete_course(id):
    c = Course.query.get_or_404(id)
    db.session.delete(c)
    db.session.commit()
    flash('Course deleted.', 'info')
    return redirect(url_for('main.courses'))

# ---------- Students CRUD ----------
@bp.route('/students')
@login_required
@role_required('professor')
def students():
    students = Student.query.order_by(Student.last_name).all()
    return render_template('students.html', students=students)

@bp.route('/students/add', methods=['GET','POST'])
@login_required
@role_required('professor')
def add_student():
    form = StudentForm()
    form.course_id.choices = [(0, '--- Select Course ---')] + [(c.id, f"{c.code} - {c.title}") for c in Course.query.order_by(Course.code)]
    if form.validate_on_submit():
        course_id = form.course_id.data if form.course_id.data != 0 else None
        s = Student(
            student_number=form.student_number.data.strip(),
            first_name=form.first_name.data.strip(),
            last_name=form.last_name.data.strip(),
            year_level=form.year_level.data,
            course_id=course_id
        )
        db.session.add(s)
        db.session.commit()
        flash('Student added.', 'success')
        return redirect(url_for('main.students'))
    return render_template('student_form.html', form=form, action='Add')

@bp.route('/students/<int:id>/edit', methods=['GET','POST'])
@login_required
@role_required('professor')
def edit_student(id):
    s = Student.query.get_or_404(id)
    form = StudentForm(obj=s)
    form.course_id.choices = [(0, '--- Select Course ---')] + [(c.id, f"{c.code} - {c.title}") for c in Course.query.order_by(Course.code)]
    if form.validate_on_submit():
        s.student_number = form.student_number.data.strip()
        s.first_name = form.first_name.data.strip()
        s.last_name = form.last_name.data.strip()
        s.year_level = form.year_level.data
        s.course_id = form.course_id.data if form.course_id.data != 0 else None
        db.session.commit()
        flash('Student updated.', 'success')
        return redirect(url_for('main.students'))
    return render_template('student_form.html', form=form, action='Edit', student=s)

@bp.route('/students/<int:id>/delete', methods=['POST'])
@login_required
@role_required('professor')
def delete_student(id):
    s = Student.query.get_or_404(id)
    db.session.delete(s)
    db.session.commit()
    flash('Student deleted.', 'info')
    return redirect(url_for('main.students'))

# assign user to student (link user account to a student)
@bp.route('/students/<int:id>/assign_user', methods=['GET','POST'])
@login_required
@role_required('professor')
def assign_user(id):
    s = Student.query.get_or_404(id)
    # show users without student_id and role student
    available_users = User.query.filter_by(role='student', student_id=None).all()
    if request.method == 'POST':
        user_id = int(request.form.get('user_id'))
        user = User.query.get(user_id)
        if user and user.role == 'student':
            user.student_id = s.id
            db.session.commit()
            flash('User assigned to student.', 'success')
            return redirect(url_for('main.students'))
    return render_template('assign_user.html', student=s, users=available_users)

# ---------- Attendance CRUD ----------
@bp.route('/attendance')
@login_required
def attendance_list():
    # students see their own attendance
    if current_user.role == 'student' and current_user.student_id:
        student = Student.query.get(current_user.student_id)
        attendances = student.attendances
        return render_template('attendance_list_student.html', attendances=attendances, student=student)
    # professors/admin see all
    page = request.args.get('page', 1, type=int)
    attendances = Attendance.query.order_by(Attendance.date.desc()).paginate(page=page, per_page=12)
    return render_template('attendance_list.html', attendances=attendances)

@bp.route('/attendance/add', methods=['GET','POST'])
@login_required
@role_required('professor')
def add_attendance():
    form = AttendanceForm()
    form.student_id.choices = [(s.id, s.full_name() + f" ({s.student_number})") for s in Student.query.order_by(Student.last_name)]
    if form.validate_on_submit():
        att = Attendance(
            student_id=form.student_id.data,
            date=form.date.data,
            status=form.status.data,
            notes=form.notes.data
        )
        db.session.add(att)
        db.session.commit()
        flash('Attendance recorded.', 'success')
        return redirect(url_for('main.attendance_list'))
    if request.method == 'GET':
        form.date.data = datetime.utcnow().date()
    return render_template('attendance_form.html', form=form, action='Add')

@bp.route('/attendance/<int:id>/edit', methods=['GET','POST'])
@login_required
@role_required('professor')
def edit_attendance(id):
    att = Attendance.query.get_or_404(id)
    form = AttendanceForm(obj=att)
    form.student_id.choices = [(s.id, s.full_name() + f" ({s.student_number})") for s in Student.query.order_by(Student.last_name)]
    if form.validate_on_submit():
        att.student_id = form.student_id.data
        att.date = form.date.data
        att.status = form.status.data
        att.notes = form.notes.data
        db.session.commit()
        flash('Attendance updated.', 'success')
        return redirect(url_for('main.attendance_list'))
    return render_template('attendance_form.html', form=form, action='Edit', attendance=att)

@bp.route('/attendance/<int:id>/delete', methods=['POST'])
@login_required
@role_required('professor')
def delete_attendance(id):
    att = Attendance.query.get_or_404(id)
    db.session.delete(att)
    db.session.commit()
    flash('Attendance deleted.', 'info')
    return redirect(url_for('main.attendance_list'))

# ---------- Reports ----------
@bp.route('/report')
@login_required
def report():
    # if student, show their own summary
    if current_user.role == 'student' and current_user.student_id:
        student = Student.query.get(current_user.student_id)
        total = len(student.attendances)
        present = len([a for a in student.attendances if a.status == 'Present'])
        percentage = round((present/total*100),2) if total else 0.0
        return render_template('report_student.html', student=student, total=total, present=present, percentage=percentage)
    # professor/admin: report per course
    courses = Course.query.order_by(Course.code).all()
    data = []
    for c in courses:
        for s in c.students:
            total = len(s.attendances)
            present = len([a for a in s.attendances if a.status == 'Present'])
            data.append({'course': c, 'student': s, 'total': total, 'present': present, 'percentage': round((present/total*100),2) if total else 0.0})
    return render_template('report.html', data=data)
