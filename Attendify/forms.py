from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, DateField
from wtforms.validators import DataRequired, Length, EqualTo, Optional

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=80)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('student','Student'), ('professor','Professor')])
    submit = SubmitField('Register')

class StudentForm(FlaskForm):
    student_number = StringField('Student Number', validators=[DataRequired(), Length(max=50)])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=100)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=100)])
    year_level = SelectField('Year Level', choices=[('1','1'),('2','2'),('3','3'),('4','4')], validators=[DataRequired()])
    course_id = SelectField('Course', coerce=int, validators=[Optional()])
    submit = SubmitField('Save')

class CourseForm(FlaskForm):
    code = StringField('Course Code', validators=[DataRequired(), Length(max=50)])
    title = StringField('Course Title', validators=[DataRequired(), Length(max=200)])
    submit = SubmitField('Save')

class AttendanceForm(FlaskForm):
    student_id = SelectField('Student', coerce=int, validators=[DataRequired()])
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    status = SelectField('Status', choices=[('Present','Present'),('Absent','Absent'),('Late','Late'),('Excused','Excused')], validators=[DataRequired()])
    notes = TextAreaField('Notes')
    submit = SubmitField('Save')
