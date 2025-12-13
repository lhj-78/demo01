from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, DateField, FloatField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo, Optional, NumberRange, ValidationError
from models import User, Student, Course, Department, Grade

class LoginForm(FlaskForm):
    username = StringField('用户名/学号', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')

class RegistrationForm(FlaskForm):
    username = StringField('用户名', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, '用户名只能包含字母、数字、点或下划线')])
    email = StringField('电子邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('密码', validators=[
        DataRequired(), 
        Length(min=6, message='密码长度至少为6个字符'),

    ])
    password2 = PasswordField('确认密码', validators=[
        DataRequired(), EqualTo('password', message='密码不匹配')])

    # 添加院系和专业下拉框
    department_id = SelectField('院系', coerce=int, validators=[DataRequired()])
    major_id = SelectField('专业', coerce=int, validators=[Optional()])

    submit = SubmitField('注册')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已被使用')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('电子邮箱已被注册')

class StudentForm(FlaskForm):
    student_id = StringField('学号', validators=[Optional(), Length(1, 20)], 
                            description="留空则自动生成")
    name = StringField('姓名', validators=[DataRequired(), Length(1, 50)])
    gender = SelectField('性别', choices=[('男', '男'), ('女', '女')], validators=[Optional()])
    # 添加院系和专业字段
    department_id = SelectField('院系', coerce=int, validators=[Optional()])
    major_id = SelectField('专业', coerce=int, validators=[Optional()])
    birth_date = DateField('出生日期', validators=[Optional()])
    phone = StringField('电话', validators=[Optional(), Length(max=20)])
    address = StringField('地址', validators=[Optional(), Length(max=200)])
    # 添加密码字段
    password = PasswordField('密码', validators=[
        Length(min=6, message='密码长度至少为6个字符'),
        Optional()
    ])
    password2 = PasswordField('确认密码', validators=[
        EqualTo('password', message='密码不匹配'),
        Optional()
    ])
    submit = SubmitField('提交')

class CourseForm(FlaskForm):
    course_code = StringField('课程代码', validators=[DataRequired(), Length(1, 20)])
    course_name = StringField('课程名称', validators=[DataRequired(), Length(1, 100)])
    credit = FloatField('学分', validators=[DataRequired(), NumberRange(min=0.1, max=10.0)])
    description = TextAreaField('课程描述', validators=[Optional()])
    submit = SubmitField('提交')

class PasswordForm(FlaskForm):
    password = PasswordField('新密码', validators=[
        DataRequired(),
        Length(min=6, message='密码长度至少为6个字符')
    ])
    password2 = PasswordField('确认密码', validators=[
        DataRequired(),
        EqualTo('password', message='密码不匹配')
    ])
    submit = SubmitField('修改密码')

class GradeForm(FlaskForm):
    student_id = SelectField('学生', coerce=int, validators=[DataRequired()])
    course_id = SelectField('课程', coerce=int, validators=[DataRequired()])
    score = FloatField('成绩', validators=[DataRequired(), NumberRange(min=0, max=100)])
    semester = StringField('学期', validators=[DataRequired(), Length(1, 20)])
    exam_date = DateField('考试日期', validators=[Optional()])
    submit = SubmitField('提交')

class DepartmentForm(FlaskForm):
    dept_code = StringField('院系代码', validators=[DataRequired(), Length(1, 20)])
    dept_name = StringField('院系名称', validators=[DataRequired(), Length(1, 100)])
    dean = StringField('院长', validators=[Optional(), Length(1, 50)])
    office_location = StringField('办公室位置', validators=[Optional(), Length(max=100)])
    phone = StringField('联系电话', validators=[Optional(), Length(max=20)])

class MajorForm(FlaskForm):
    major_code = StringField('专业代码', validators=[DataRequired(), Length(1, 20)])
    major_name = StringField('专业名称', validators=[DataRequired(), Length(1, 100)])
    dept_id = SelectField('所属院系', coerce=int, validators=[DataRequired()])
    submit = SubmitField('提交')

class AdminForm(FlaskForm):
    username = StringField('用户名', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, '用户名只能包含字母、数字、点或下划线')])
    email = StringField('电子邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('密码', validators=[
        DataRequired(),
        Length(min=6, message='密码长度至少为6个字符')])
    password2 = PasswordField('确认密码', validators=[
        DataRequired(), EqualTo('password', message='密码不匹配')])
    submit = SubmitField('创建管理员')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已被使用')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('电子邮箱已被注册')
