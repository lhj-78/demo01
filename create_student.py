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
        if User.query.filter_by(username=student_id).first():
            flash('用户名已存在，请使用其他学号', 'error')
            return render_template('students/form.html', form=form, title='添加学生')

        # 如果提供了密码，使用提供的密码，否则使用默认密码
        password = form.password.data if form.password.data else "123456"

        try:
            # 创建新用户
            user = User(username=student_id, email=f"{student_id}@example.com")
            user.set_password(password)

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
