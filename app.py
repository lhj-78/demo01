from flask import Flask, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from models import db, User, Student, Course, Grade, Department, Major
from forms import LoginForm, RegistrationForm, StudentForm, CourseForm, GradeForm, DepartmentForm, AdminForm, PasswordForm
from datetime import datetime, timedelta
from sqlalchemy.orm import joinedload

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a-very-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///student_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_TIME_LIMIT'] = None
# 设置会话超时时间为10分钟
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=3)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = '请先登录以访问此页面。'
login_manager.login_message_category = 'info'

# 初始化CSRF保护
csrf = CSRFProtect(app)

@login_manager.user_loader
def load_user(user_id):
    if user_id is not None:
        return User.query.get(int(user_id))
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/init_admin')
def init_admin():
    # 创建管理员用户
    admin = User(username='admin', email='admin@example.com')
    admin.set_password('admin123')
    admin.is_admin = True
    db.session.add(admin)
    db.session.commit()
    return '管理员用户已创建，用户名: admin, 密码: admin123'

@app.route('/login', methods=['GET', 'POST'])
def login():
    # 检查用户是否已经登录
    if current_user.is_authenticated:
        # 如果是管理员，直接跳转到管理员仪表板
        if current_user.is_admin:
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        # 首先尝试通过学号查找学生
        student = Student.query.filter_by(student_id=form.username.data).first()
        user = None

        # 如果找到学生记录，获取关联的用户
        if student and student.user:
            user = student.user
            print(f"通过学号找到用户: {user.username}")  # 调试信息
        else:
            # 如果通过学号找不到，尝试通过用户名查找
            user = User.query.filter_by(username=form.username.data).first()
            print(f"通过用户名找到用户: {user.username if user else 'None'}")  # 调试信息

        if user is None or not user.check_password(form.password.data):
            flash('用户名/学号或密码错误')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)
        
        # 设置会话为永久性会话，应用超时设置
        from flask import session
        session.permanent = True

        # 根据用户类型跳转到不同的仪表板
        if user.is_admin:
            flash(f'欢迎回来，管理员 {user.username}！', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash(f'欢迎回来，{user.username}！', 'success')
            return redirect(url_for('dashboard'))

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/reset_password', methods=['POST'])
def reset_password():
    username = request.form.get('username')
    
    if not username:
        return jsonify({'success': False, 'message': '请提供用户名或学号'})
    
    try:
        # 首先尝试通过学号查找学生
        student = Student.query.filter_by(student_id=username).first()
        user = None
        
        # 如果找到学生记录，获取关联的用户
        if student and student.user:
            user = student.user
        else:
            # 如果通过学号找不到，尝试通过用户名查找
            user = User.query.filter_by(username=username).first()
        
        if user is None:
            return jsonify({'success': False, 'message': '用户不存在'})
        
        # 重置密码为123456
        user.set_password('123456')
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'重置密码失败: {str(e)}'})

@app.route('/register', methods=['GET', 'POST'])
def register():
    # 如果用户已经登录，重定向到仪表板
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    # 创建注册表单实例
    form = RegistrationForm()

    # 填充院系和专业的下拉框选项
    from models import Department, Major
    departments = Department.query.all()
    form.department_id.choices = [(0, '请选择院系')] + [(d.id, d.dept_name) for d in departments]

    # 如果有院系，则获取第一个院系的专业列表作为初始选项
    if departments:
        first_dept_id = departments[0].id
        majors = Major.query.filter_by(dept_id=first_dept_id).all()
        if majors:
            form.major_id.choices = [(0, '请选择专业')] + [(m.id, m.major_name) for m in majors]
        else:
            form.major_id.choices = [(0, '该院系暂无专业')]
    else:
        form.major_id.choices = [(0, '请先添加院系')]

    # 处理表单提交
    if request.method == 'POST':
        # 手动验证表单数据
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        password2 = request.form.get('password2', '')
        department_id = request.form.get('department_id', type=int)
        major_id = request.form.get('major_id', type=int)

        # 基本验证
        if not username or not email or not password or not password2:
            flash('所有字段都是必填的', 'error')
            return render_template('register.html', form=form)

        # 验证院系和专业
        if department_id == 0:
            flash('请选择院系', 'error')
            return render_template('register.html', form=form)

        if password != password2:
            flash('两次输入的密码不匹配', 'error')
            return render_template('register.html', form=form)

        if len(password) < 6:
            flash('密码长度至少为6个字符', 'error')
            return render_template('register.html', form=form)

        try:
            # 检查用户名和邮箱是否已存在
            if User.query.filter_by(username=username).first():
                flash('用户名已被使用', 'error')
                return render_template('register.html', form=form)

            if User.query.filter_by(email=email).first():
                flash('电子邮箱已被注册', 'error')
                return render_template('register.html', form=form)

            # 创建新用户
            user = User(username=username, email=email)
            user.set_password(password)

            # 添加到数据库并提交以获取用户ID
            db.session.add(user)
            db.session.commit()

            # 检查用户是否是管理员，如果是，则不创建学生记录
            if not user.is_admin:
                # 生成唯一学号
                import time
                timestamp_suffix = str(int(time.time()))[-4:]
                student_id = f"STU{user.id}{timestamp_suffix}"

                # 创建学生信息记录
                student = Student(
                    user_id=user.id,
                    student_id=student_id,
                    name=username,
                    dept_id=department_id if department_id > 0 else None,
                    major_id=major_id if major_id > 0 else None
                )

                # 添加学生记录并提交
                db.session.add(student)
                db.session.commit()

            # 显示成功消息并重定向到登录页面
            flash('注册成功！请登录后完善个人信息。', 'success')
            return redirect(url_for('login'))

        except Exception as e:
            # 如果发生错误，回滚事务并显示错误消息
            db.session.rollback()
            flash(f'注册失败: {str(e)}', 'error')
            print(f"注册错误: {str(e)}")  # 添加调试输出

    # 显示注册表单
    return render_template('register.html', form=form, departments=departments)

@app.route('/dashboard')
@login_required
def dashboard():
    # 普通用户仪表板
    student = Student.query.filter_by(user_id=current_user.id).first()
    return render_template('user_dashboard.html', student=student)

@app.route('/schedule')
@login_required
def schedule():
    # 课表页面
    student = Student.query.filter_by(user_id=current_user.id).first()
    return render_template('student_schedule_final.html', student=student)

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    # 确保只有管理员可以访问
    if not current_user.is_admin:
        abort(403)

    # 获取统计数据
    # 管理员数量
    admin_count = User.query.filter(User.is_admin == True).count()
    # 只统计非管理员用户对应的学生
    student_count = Student.query.join(User).filter(User.is_admin == False).count()
    course_count = Course.query.count()

    return render_template('admin_dashboard.html', 
                          admin_count=admin_count, 
                          student_count=student_count, 
                          course_count=course_count)

# 管理员路由
@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        abort(403)
    return render_template('admin.html')

# 用户管理
@app.route('/admin/users')
@login_required
def list_users():
    if not current_user.is_admin:
        abort(403)
    # 只获取管理员用户
    users = User.query.filter(User.is_admin == True).all()
    admin_count = User.query.filter(User.is_admin == True).count()
    return render_template('users/list.html', users=users, user_count=admin_count)

@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        abort(403)
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('用户已删除')
    return redirect(url_for('list_users'))

# 创建管理员
@app.route('/admin/admins/new', methods=['GET', 'POST'])
@login_required
def create_admin():
    # 检查当前用户是否是管理员
    if not current_user.is_admin:
        abort(403)
    
    # 处理表单提交
    if request.method == 'POST':
        # 获取表单数据
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        
        # 基本验证
        if not username or not email or not password or not password2:
            flash('所有字段都是必填的', 'error')
            return render_template('admins/form.html', title='创建管理员')
        
        if password != password2:
            flash('两次输入的密码不匹配', 'error')
            return render_template('admins/form.html', title='创建管理员')
        
        if len(password) < 6:
            flash('密码长度至少为6个字符', 'error')
            return render_template('admins/form.html', title='创建管理员')
        
        # 检查用户名和邮箱是否已存在
        if User.query.filter_by(username=username).first():
            flash('用户名已被使用', 'error')
            return render_template('admins/form.html', title='创建管理员')
        
        if User.query.filter_by(email=email).first():
            flash('电子邮箱已被注册', 'error')
            return render_template('admins/form.html', title='创建管理员')
        
        try:
            # 创建新管理员用户
            admin = User(
                username=username,
                email=email,
                is_admin=True
            )
            # 设置密码
            admin.set_password(password)
            # 添加到数据库
            db.session.add(admin)
            db.session.commit()
            # 显示成功消息
            flash('管理员创建成功！')
            # 重定向到管理员列表页面
            return redirect(url_for('list_users'))
        except Exception as e:
            # 如果发生错误，回滚事务并显示错误消息
            db.session.rollback()
            flash(f'创建管理员时出错: {str(e)}', 'error')
    
    # 如果是GET请求或表单验证失败，显示表单页面
    return render_template('admins/form.html', title='创建管理员')

# 学生管理
@app.route('/admin/students')
@login_required
def list_students():
    print(f"当前用户: {current_user.username}, 是否为管理员: {current_user.is_admin}")
    # 暂时允许所有登录用户访问学生列表
    # if not current_user.is_admin:
    #     abort(403)
    # 获取所有学生记录，排除管理员账户
    students = Student.query.join(User).filter(User.is_admin == False).all()
    # 获取所有院系
    departments = Department.query.all()
    return render_template('students/list.html', students=students, departments=departments)

@app.route('/admin/students/new', methods=['GET', 'POST'])
@login_required
def create_student():
    if not current_user.is_admin:
        abort(403)
    form = StudentForm()
    if form.validate_on_submit():
        # 如果没有提供学号，自动生成一个
        if not form.student_id.data:
            # 获取当前年份后两位
            from datetime import datetime
            year = datetime.now().strftime('%y')
            # 查询当前年份的学生数量
            count = Student.query.filter(Student.student_id.like(f'STU{year}%')).count()
            # 生成新的学号，格式为STU+年份后两位+4位序号
            student_id = f"STU{year}{count+1:04d}"
        else:
            student_id = form.student_id.data

        # 检查学号是否已存在
        if Student.query.filter_by(student_id=student_id).first():
            flash('学号已存在，请重新输入', 'error')
            return render_template('students/form.html', form=form, title='添加学生')

        # 检查用户名是否已存在
        existing_user = User.query.filter_by(username=student_id).first()
        if existing_user:
            # 检查是否有关联的学生记录
            if not existing_user.student_info:
                # 如果没有关联的学生记录，说明是已删除的学生，可以复用用户名
                db.session.delete(existing_user)
                db.session.commit()
                flash('检测到已删除的学生记录，已清理相关数据', 'info')
            else:
                # 如果有关联的学生记录，说明学号已被使用
                flash('学号已存在，请使用其他学号', 'error')
                return render_template('students/form.html', form=form, title='添加学生')

        # 固定使用默认密码123456
        password = "123456"

        try:
            # 创建新用户
            user = User(username=student_id, email=f"{student_id}@example.com", is_admin=False)
            user.set_password(password)
        
            # 用户已添加到会话中，无需再次添加
        
            # 创建学生信息记录
            student = Student(
                user=user,  # 使用关联对象而不是ID
                student_id=student_id,
                name=form.name.data,
                gender=form.gender.data,
                birth_date=form.birth_date.data,
                phone=form.phone.data,
                address=form.address.data
            )

            # 一次性添加到数据库
            db.session.add(user)
            db.session.add(student)
            db.session.commit()
            flash(f'学生信息已添加，学号为：{student_id}，登录密码为：{password}')
            return redirect(url_for('list_students'))

        except Exception as e:
            db.session.rollback()
            flash(f'添加学生时出错: {str(e)}', 'error')
            return render_template('students/form.html', form=form, title='添加学生')
    return render_template('students/form.html', form=form, title='添加学生')

@app.route('/admin/students/<int:student_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_student(student_id):
    if not current_user.is_admin:
        abort(403)
    student = Student.query.get_or_404(student_id)
    
    # 检查关联的用户是否是管理员
    if student.user and student.user.is_admin:
        flash('不能编辑管理员的学生信息！', 'error')
        return redirect(url_for('list_students'))
    
    form = StudentForm(obj=student)

    # 填充院系和专业下拉框选项
    form.department_id.choices = [(0, '请选择院系')] + [(d.id, d.dept_name) for d in Department.query.all()]
    form.major_id.choices = [(0, '请选择专业')] + [(m.id, m.major_name) for m in Major.query.all()]

    if form.validate_on_submit():
        student.student_id = form.student_id.data
        student.name = form.name.data
        student.gender = form.gender.data
        student.birth_date = form.birth_date.data
        student.phone = form.phone.data
        student.address = form.address.data

        # 更新院系和专业
        if form.department_id.data and form.department_id.data != 0:
            student.dept_id = form.department_id.data
        else:
            student.dept_id = None

        if form.major_id.data and form.major_id.data != 0:
            student.major_id = form.major_id.data
        else:
            student.major_id = None

        # 如果提供了新密码，更新密码
        if form.password.data:
            student.user.set_password(form.password.data)
            flash('学生信息、院系专业和密码已更新')
        else:
            flash('学生信息和院系专业已更新')

        db.session.commit()
        return redirect(url_for('list_students'))
    return render_template('students/form.html', form=form, title='编辑学生')

# 更新学生院系和专业
# API端点：获取院系和专业数据
@app.route('/api/departments_majors')
@login_required
def get_departments_majors():
    if not current_user.is_admin:
        return jsonify({'error': '无权访问'}), 403

    departments = Department.query.all()
    majors = Major.query.all()

    return jsonify({
        'departments': [{'id': d.id, 'dept_name': d.dept_name} for d in departments],
        'majors': [{'id': m.id, 'major_name': m.major_name, 'dept_id': m.dept_id} for m in majors]
    })

@app.route('/admin/students/<int:student_id>/update_dept', methods=['POST'])
@login_required
def update_student_dept(student_id):
    if not current_user.is_admin:
        abort(403)

    student = Student.query.get_or_404(student_id)

    # 检查关联的用户是否是管理员
    if student.user and student.user.is_admin:
        flash('不能修改管理员学生的院系和专业！', 'error')
        return redirect(url_for('list_students'))

    dept_id = request.form.get('dept_id')
    major_id = request.form.get('major_id')
    delete_dept = request.form.get('delete_dept') == 'on'
    delete_major = request.form.get('delete_major') == 'on'

    # 更新院系
    if delete_dept:
        student.dept_id = None
        # 如果删除了院系，也删除专业
        student.major_id = None
    elif dept_id:
        student.dept_id = dept_id

    # 更新专业
    if delete_major:
        student.major_id = None
    elif major_id and not delete_dept:  # 只有在没有删除院系的情况下才更新专业
        student.major_id = major_id

    db.session.commit()
    flash('学生院系和专业已更新')
    return redirect(url_for('list_students'))

@app.route('/admin/students/<int:student_id>/password', methods=['GET', 'POST'])
@login_required
def change_student_password(student_id):
    if not current_user.is_admin:
        abort(403)

    student = Student.query.get_or_404(student_id)

    # 检查关联的用户是否是管理员
    if student.user and student.user.is_admin:
        flash('不能修改管理员的密码！', 'error')
        return redirect(url_for('list_students'))

    form = PasswordForm()
    if form.validate_on_submit():
        student.user.set_password(form.password.data)
        db.session.commit()
        flash(f'{student.name}的密码已成功修改')
        return redirect(url_for('list_students'))

    return render_template('students/password.html', form=form, student=student, title='修改学生密码')

@app.route('/admin/students/<int:student_id>/delete', methods=['POST'])
@login_required
@csrf.exempt
def delete_student(student_id):
    if not current_user.is_admin:
        abort(403)
    student = Student.query.get_or_404(student_id)
    
    # 检查关联的用户是否是管理员
    if student.user and student.user.is_admin:
        flash('不能删除管理员的学生信息！', 'error')
        return redirect(url_for('list_students'))
    
    # 获取关联的用户ID，以便后续删除
    user_id = student.user_id if student.user else None

    # 删除学生的成绩记录
    Grade.query.filter_by(student_id=student.id).delete()

    # 删除学生的选课记录
    student.courses = []  # 清空关联的课程

    # 删除学生记录
    db.session.delete(student)

    # 如果有关联的用户，也删除用户记录
    if user_id:
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)

    db.session.commit()
    flash('学生信息及相关账户已删除')
    return redirect(url_for('list_students'))

# 课程管理
@app.route('/admin/courses')
@login_required
def list_courses():
    if not current_user.is_admin:
        abort(403)
    courses = Course.query.all()
    return render_template('courses/list.html', courses=courses)

@app.route('/admin/courses/new', methods=['GET', 'POST'])
@login_required
def create_course():
    if not current_user.is_admin:
        abort(403)
    form = CourseForm()
    if form.validate_on_submit():
        course = Course(
            course_code=form.course_code.data,
            course_name=form.course_name.data,
            credit=form.credit.data,
            description=form.description.data
        )
        db.session.add(course)
        db.session.commit()
        flash('课程已添加')
        return redirect(url_for('list_courses'))
    return render_template('courses/form.html', form=form, title='添加课程')

@app.route('/admin/courses/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    if not current_user.is_admin:
        abort(403)
    course = Course.query.get_or_404(course_id)
    form = CourseForm(obj=course)
    if form.validate_on_submit():
        course.course_code = form.course_code.data
        course.course_name = form.course_name.data
        course.credit = form.credit.data
        course.description = form.description.data
        db.session.commit()
        flash('课程信息已更新')
        return redirect(url_for('list_courses'))
    return render_template('courses/form.html', form=form, title='编辑课程')

@app.route('/admin/courses/<int:course_id>/delete', methods=['POST'])
@login_required
def delete_course(course_id):
    if not current_user.is_admin:
        abort(403)
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    flash('课程已删除')
    return redirect(url_for('list_courses'))

# 成绩管理
@app.route('/admin/grades')
@login_required
def list_grades():
    if not current_user.is_admin:
        abort(403)
    grades = Grade.query.all()
    return render_template('grades/list.html', grades=grades)

@app.route('/admin/grades/new', methods=['GET', 'POST'])
@login_required
def create_grade():
    if not current_user.is_admin:
        abort(403)
    form = GradeForm()
    # 只列出非管理员用户对应的学生，排除关联管理员（如 admin1）
    form.student_id.choices = [(s.id, f"{s.name} ({s.student_id})") for s in Student.query.join(User).filter(User.is_admin == False).all()]
    form.course_id.choices = [(c.id, f"{c.course_name} ({c.course_code})") for c in Course.query.all()]

    if form.validate_on_submit():
        grade = Grade(
            student_id=form.student_id.data,
            course_id=form.course_id.data,
            score=form.score.data,
            semester=form.semester.data,
            exam_date=form.exam_date.data
        )
        db.session.add(grade)
        db.session.commit()
        flash('成绩已添加')
        return redirect(url_for('list_grades'))
    return render_template('grades/form.html', form=form, title='添加成绩')

@app.route('/admin/grades/<int:grade_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_grade(grade_id):
    if not current_user.is_admin:
        abort(403)
    grade = Grade.query.get_or_404(grade_id)
    form = GradeForm(obj=grade)
    # 只列出非管理员用户对应的学生，排除关联管理员（如 admin1）
    form.student_id.choices = [(s.id, f"{s.name} ({s.student_id})") for s in Student.query.join(User).filter(User.is_admin == False).all()]
    form.course_id.choices = [(c.id, f"{c.course_name} ({c.course_code})") for c in Course.query.all()]

    if form.validate_on_submit():
        grade.student_id = form.student_id.data
        grade.course_id = form.course_id.data
        grade.score = form.score.data
        grade.semester = form.semester.data
        grade.exam_date = form.exam_date.data
        db.session.commit()
        flash('成绩信息已更新')
        return redirect(url_for('list_grades'))
    return render_template('grades/form.html', form=form, title='编辑成绩')

@app.route('/admin/grades/<int:grade_id>/delete', methods=['POST'])
@login_required
def delete_grade(grade_id):
    if not current_user.is_admin:
        abort(403)
    grade = Grade.query.get_or_404(grade_id)
    db.session.delete(grade)
    db.session.commit()
    flash('成绩已删除')
    return redirect(url_for('list_grades'))

# 院系管理
@app.route('/admin/departments')
@login_required
def list_departments():
    if not current_user.is_admin:
        abort(403)
    departments = Department.query.all()
    return render_template('departments/list.html', departments=departments)

@app.route('/admin/departments/new', methods=['GET', 'POST'])
@login_required
def create_department():
    if not current_user.is_admin:
        abort(403)
    form = DepartmentForm()
    if form.validate_on_submit():
        department = Department(
            dept_code=form.dept_code.data,
            dept_name=form.dept_name.data,
            dean=form.dean.data,
            office_location=form.office_location.data,
            phone=form.phone.data
        )
        db.session.add(department)
        db.session.commit()
        flash('院系信息已添加')
        return redirect(url_for('list_departments'))
    return render_template('departments/form.html', form=form, title='添加院系')

@app.route('/admin/departments/<int:dept_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_department(dept_id):
    if not current_user.is_admin:
        abort(403)
    department = Department.query.get_or_404(dept_id)
    form = DepartmentForm(obj=department)
    if form.validate_on_submit():
        department.dept_code = form.dept_code.data
        department.dept_name = form.dept_name.data
        department.dean = form.dean.data
        department.office_location = form.office_location.data
        department.phone = form.phone.data
        db.session.commit()
        flash('院系信息已更新')
        return redirect(url_for('list_departments'))
    return render_template('departments/form.html', form=form, title='编辑院系')

@app.route('/admin/departments/<int:dept_id>/delete', methods=['POST'])
@login_required
def delete_department(dept_id):
    if not current_user.is_admin:
        abort(403)
    department = Department.query.get_or_404(dept_id)
    db.session.delete(department)
    db.session.commit()
    flash('院系信息已删除')
    return redirect(url_for('list_departments'))

# 用户个人信息管理
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        # 如果没有学生信息，则创建一个
        student = Student(user_id=current_user.id, student_id=str(current_user.id), name=current_user.username)
        db.session.add(student)
        db.session.commit()

    # 填充院系和专业下拉框选项
    departments = Department.query.all()
    
    form = StudentForm(obj=student)
    form.department_id.choices = [(0, '请选择院系')] + [(d.id, d.dept_name) for d in departments]
    
    # 如果有院系，则获取第一个院系的专业列表作为初始选项
    if departments:
        first_dept_id = departments[0].id
        majors = Major.query.filter_by(dept_id=first_dept_id).all()
        if majors:
            form.major_id.choices = [(0, '请选择专业')] + [(m.id, m.major_name) for m in majors]
        else:
            form.major_id.choices = [(0, '该院系暂无专业')]
    else:
        form.major_id.choices = [(0, '请先添加院系')]
    
    # 如果学生已有院系，则更新专业选项
    if student and student.dept_id:
        majors = Major.query.filter_by(dept_id=student.dept_id).all()
        if majors:
            form.major_id.choices = [(0, '请选择专业')] + [(m.id, m.major_name) for m in majors]
            # 设置当前选中的专业
            if student.major_id:
                form.major_id.data = student.major_id
        
        # 设置当前选中的院系
        form.department_id.data = student.dept_id
    
    if form.validate_on_submit():
        student.student_id = form.student_id.data
        student.name = form.name.data
        student.gender = form.gender.data
        student.birth_date = form.birth_date.data
        student.phone = form.phone.data
        student.address = form.address.data
        
        # 更新院系和专业
        if form.department_id.data and form.department_id.data != 0:
            student.dept_id = form.department_id.data
        else:
            student.dept_id = None
            
        if form.major_id.data and form.major_id.data != 0:
            student.major_id = form.major_id.data
        else:
            student.major_id = None
        
        # 如果提供了新密码，更新密码
        if form.password.data:
            current_user.set_password(form.password.data)
            flash('个人信息和密码已更新，请重新登录！')
            logout_user()
            return redirect(url_for('login'))
        else:
            flash('个人信息已更新')
            
        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('profile.html', form=form, student=student)

# API路由：获取院系下的专业列表
@app.route('/api/departments/<int:dept_id>/majors')
@login_required
def get_department_majors(dept_id):
    if not current_user.is_admin:
        abort(403)

    department = Department.query.get_or_404(dept_id)
    majors = [{'id': major.id, 'major_name': major.major_name} for major in department.majors]
    return jsonify(majors)

# 查看个人成绩
@app.route('/my_grades')
@login_required
def my_grades():
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        flash('请先完善个人信息')
        return redirect(url_for('profile'))

    grades = Grade.query.filter_by(student_id=student.id).all()
    return render_template('my_grades.html', grades=grades)

# 管理员修改密码
@app.route('/admin/change_password', methods=['GET', 'POST'])
@login_required
def admin_change_password():
    # 确保只有管理员可以访问
    if not current_user.is_admin:
        abort(403)
    
    form = PasswordForm()
    if form.validate_on_submit():
        current_user.set_password(form.password.data)
        db.session.commit()
        flash('密码已成功修改，请重新登录！')
        # 修改密码后强制退出登录
        logout_user()
        return redirect(url_for('login'))
    
    return render_template('admin_change_password.html', form=form, title='修改密码')

# 获取专业列表API
@app.route('/api/majors/<int:department_id>')
def get_majors_by_department(department_id):
    from models import Major, Department
    print(f"API请求: 院系ID={department_id}")

    # 检查院系是否存在
    department = Department.query.get(department_id)
    if not department:
        print(f"院系不存在: ID={department_id}")
        return jsonify([])

    print(f"找到院系: {department.dept_name}")

    # 获取该院系下的所有专业
    majors = Major.query.filter_by(dept_id=department_id).all()
    print(f"该院系下有 {len(majors)} 个专业")

    result = [{'id': major.id, 'major_name': major.major_name} for major in majors]
    print(f"返回的专业列表: {result}")
    return jsonify(result)

# 测试API页面
@app.route('/test_api')
def test_api():
    with open('test_api.html', 'r', encoding='utf-8') as f:
        return f.read()

# 测试API直接页面
@app.route('/test_api_direct')
def test_api_direct():
    with open('test_api_direct.html', 'r', encoding='utf-8') as f:
        return f.read()

# 测试API简单页面
@app.route('/test_api_simple')
def test_api_simple():
    with open('test_api_simple.html', 'r', encoding='utf-8') as f:
        return f.read()

# 测试院系和专业关联页面
@app.route('/test_majors')
def test_majors():
    return render_template('test_majors.html')

# 测试注册页院系和专业关联页面
@app.route('/test_register_majors')
def test_register_majors():
    return render_template('test_register_majors.html')

# 测试下拉框联动页面
@app.route('/test_dropdown')
def test_dropdown():
    from models import Department
    departments = Department.query.all()
    return render_template('test_dropdown.html', departments=departments)

# 测试注册页下拉框联动页面
@app.route('/test_register_dropdown')
def test_register_dropdown():
    with open('test_register_dropdown.html', 'r', encoding='utf-8') as f:
        return f.read()

# 测试API Fetch页面
@app.route('/test_api_fetch')
def test_api_fetch():
    with open('test_api_fetch.html', 'r', encoding='utf-8') as f:
        return f.read()

# 测试注册页面
@app.route('/test_register_simple')
def test_register_simple():
    with open('test_register_simple.html', 'r', encoding='utf-8') as f:
        return f.read()

# 测试注册页面调试
@app.route('/test_register_debug')
def test_register_debug():
    with open('test_register_debug.html', 'r', encoding='utf-8') as f:
        return f.read()

# 测试注册页面最终版
@app.route('/test_register_final')
def test_register_final():
    from models import Department
    departments = Department.query.all()
    return render_template('test_register_final.html', departments=departments)



# 专业管理
@app.route('/majors')
@login_required
def list_majors():
    # 确保只有管理员可以访问
    if not current_user.is_admin:
        abort(403)

    from models import Major
    majors = Major.query.all()
    return render_template('majors/list.html', majors=majors)

@app.route('/majors/create', methods=['GET', 'POST'])
@login_required
def create_major():
    # 确保只有管理员可以访问
    if not current_user.is_admin:
        abort(403)

    from models import Department, Major
    from forms import MajorForm

    form = MajorForm()
    form.dept_id.choices = [(d.id, d.dept_name) for d in Department.query.all()]

    if form.validate_on_submit():
        # 检查专业代码是否已存在
        if Major.query.filter_by(major_code=form.major_code.data).first():
            flash('专业代码已存在', 'error')
            return render_template('majors/form.html', form=form, title='添加专业')

        # 创建新专业
        major = Major(
            major_code=form.major_code.data,
            major_name=form.major_name.data,
            dept_id=form.dept_id.data
        )

        db.session.add(major)
        db.session.commit()

        flash('专业添加成功', 'success')
        return redirect(url_for('list_majors'))

    return render_template('majors/form.html', form=form, title='添加专业')

@app.route('/majors/edit/<int:major_id>', methods=['GET', 'POST'])
@login_required
def edit_major(major_id):
    # 确保只有管理员可以访问
    if not current_user.is_admin:
        abort(403)

    from models import Department, Major
    from forms import MajorForm

    major = Major.query.get_or_404(major_id)
    form = MajorForm(obj=major)
    form.dept_id.choices = [(d.id, d.dept_name) for d in Department.query.all()]

    if form.validate_on_submit():
        # 检查专业代码是否已被其他专业使用
        existing_major = Major.query.filter_by(major_code=form.major_code.data).first()
        if existing_major and existing_major.id != major_id:
            flash('专业代码已被其他专业使用', 'error')
            return render_template('majors/form.html', form=form, title='编辑专业')

        # 更新专业信息
        major.major_code = form.major_code.data
        major.major_name = form.major_name.data
        major.dept_id = form.dept_id.data

        db.session.commit()

        flash('专业信息更新成功', 'success')
        return redirect(url_for('list_majors'))

    return render_template('majors/form.html', form=form, title='编辑专业')

@app.route('/majors/delete/<int:major_id>', methods=['POST'])
@login_required
def delete_major(major_id):
    # 确保只有管理员可以访问
    if not current_user.is_admin:
        abort(403)

    from models import Major

    major = Major.query.get_or_404(major_id)

    try:
        db.session.delete(major)
        db.session.commit()
        flash('专业删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除专业失败: {str(e)}', 'error')

    return redirect(url_for('list_majors'))

# 学生修改密码
@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    # 确保只有学生（非管理员）可以访问
    if current_user.is_admin:
        abort(403)
    
    form = PasswordForm()
    if form.validate_on_submit():
        current_user.set_password(form.password.data)
        db.session.commit()
        flash('密码已成功修改，请重新登录！')
        # 修改密码后强制退出登录
        logout_user()
        return redirect(url_for('login'))
    
    return render_template('change_password.html', form=form, title='修改密码')

# 初始化数据库和创建管理员
def init_db():
    with app.app_context():
        db.create_all()

        # 检查是否已有管理员
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            # 创建管理员账户
            admin = User(
                username='admin',
                email='admin@example.com',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)

            # 创建示例数据
            dept1 = Department(dept_code='CS', dept_name='计算机科学系', dean='张教授', office_location='信息楼A101', phone='12345678')
            dept2 = Department(dept_code='EE', dept_name='电子工程系', dean='李教授', office_location='工程楼B201', phone='87654321')
            db.session.add(dept1)
            db.session.add(dept2)

            course1 = Course(course_code='CS101', course_name='计算机基础', credit=3.0, description='计算机基础知识入门')
            course2 = Course(course_code='CS102', course_name='数据结构', credit=4.0, description='数据结构与算法')
            course3 = Course(course_code='EE101', course_name='电路基础', credit=3.5, description='电路分析基础')
            db.session.add(course1)
            db.session.add(course2)
            db.session.add(course3)

            # 创建专业数据
            major1 = Major(major_code='CS01', major_name='计算机科学与技术', dept_id=dept1.id)
            major2 = Major(major_code='CS02', major_name='软件工程', dept_id=dept1.id)
            major3 = Major(major_code='EE01', major_name='电子信息工程', dept_id=dept2.id)
            major4 = Major(major_code='EE02', major_name='通信工程', dept_id=dept2.id)
            db.session.add(major1)
            db.session.add(major2)
            db.session.add(major3)
            db.session.add(major4)

            db.session.commit()

if __name__ == '__main__':
    init_db()  # 初始化数据库
    app.run(debug=True)
