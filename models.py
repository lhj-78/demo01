
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
        # 使用pbkdf2:sha256算法哈希密码
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        try:
            # 尝试使用常规方式验证密码
            return check_password_hash(self.password_hash, password)
        except ValueError:
            # 如果遇到不支持的哈希格式，返回False
            return False

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

    # 添加院系和专业字段
    dept_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=True)
    major_id = db.Column(db.Integer, db.ForeignKey('major.id'), nullable=True)

    # 关联到院系
    department = db.relationship('Department', backref='students', foreign_keys=[dept_id])

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
    # 添加与专业的关联
    major_id = db.Column(db.Integer, db.ForeignKey('major.id'), nullable=True)
    
    # 关联到专业
    major = db.relationship('Major', backref='courses')

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
    score = db.Column(db.Float, nullable=True)
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

    # 关联到专业
    majors = db.relationship('Major', backref='department', lazy=True)

    def __repr__(self):
        return f'<Department {self.dept_name}>'

# 专业表
class Major(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    major_code = db.Column(db.String(20), unique=True, nullable=False)
    major_name = db.Column(db.String(100), nullable=False)
    dept_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)

    # 关联到学生
    students = db.relationship('Student', backref='major', lazy=True)

    def __repr__(self):
        return f'<Major {self.major_name}>'
