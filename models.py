
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

# 用户表
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关联到学生信息
    student_info = db.relationship('Student', backref='user', uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

# 学生信息表
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10))
    birth_date = db.Column(db.Date)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    enrollment_date = db.Column(db.Date, default=datetime.utcnow().date)

    # 关联到课程
    courses = db.relationship('Course', secondary='student_course', backref='students')

    def __repr__(self):
        return f'<Student {self.name}>'

# 课程表
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(20), unique=True, nullable=False)
    course_name = db.Column(db.String(100), nullable=False)
    credit = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)

    def __repr__(self):
        return f'<Course {self.course_name}>'

# 学生选课关联表
student_course = db.Table('student_course',
    db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True),
    db.Column('grade', db.Float),
    db.Column('semester', db.String(20))
)

# 成绩表
class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    exam_date = db.Column(db.Date, default=datetime.utcnow().date)
    semester = db.Column(db.String(20), nullable=False)

    # 关联到学生和课程
    student = db.relationship('Student', backref=db.backref('grades', lazy=True))
    course = db.relationship('Course', backref=db.backref('grades', lazy=True))

    def __repr__(self):
        return f'<Grade {self.student_id}-{self.course_id}: {self.score}>'

# 院系表
class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dept_code = db.Column(db.String(20), unique=True, nullable=False)
    dept_name = db.Column(db.String(100), nullable=False)
    dean = db.Column(db.String(50))
    office_location = db.Column(db.String(100))
    phone = db.Column(db.String(20))

    def __repr__(self):
        return f'<Department {self.dept_name}>'
