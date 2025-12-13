
from app import app, db
from models import Department, Major

def init_departments_and_majors():
    """初始化院系和专业数据"""
    with app.app_context():
        # 检查数据库表是否存在
        from sqlalchemy import inspect
        inspector = inspect(db.engine)

        # 检查department表是否存在
        if 'department' not in inspector.get_table_names():
            print("创建department表...")
            db.create_all()

        # 检查major表是否存在
        if 'major' not in inspector.get_table_names():
            print("创建major表...")
            db.create_all()
        # 检查院系是否已存在，不存在才创建
        dept_codes = ['CS', 'EE', 'MA', 'PH']
        dept_names = ['计算机科学系', '电子工程系', '数学系', '物理系']
        dept_deans = ['张教授', '李教授', '王教授', '赵教授']
        dept_locations = ['信息楼A101', '工程楼B201', '理学楼C301', '理学楼D401']
        dept_phones = ['12345678', '87654321', '11223344', '55667788']

        departments = []

        for i, code in enumerate(dept_codes):
            dept = Department.query.filter_by(dept_code=code).first()
            if not dept:
                dept = Department(
                    dept_code=code, 
                    dept_name=dept_names[i], 
                    dean=dept_deans[i], 
                    office_location=dept_locations[i], 
                    phone=dept_phones[i]
                )
                departments.append(dept)
                print(f"创建院系: {dept_names[i]}")
            else:
                departments.append(dept)
                print(f"院系已存在: {dept_names[i]}")

        # 添加到数据库
        for dept in departments:
            if not dept.id:
                db.session.add(dept)

        db.session.commit()

        # 创建专业
        major_codes = ['CS01', 'CS02', 'CS03', 'EE01', 'EE02', 'MA01', 'MA02', 'PH01', 'PH02']
        major_names = ['计算机科学与技术', '软件工程', '人工智能', '电子信息工程', '通信工程', '基础数学', '应用数学', '理论物理', '应用物理']
        major_dept_ids = [
            departments[0].id, departments[0].id, departments[0].id,  # 计算机科学系的专业
            departments[1].id, departments[1].id,  # 电子工程系的专业
            departments[2].id, departments[2].id,  # 数学系的专业
            departments[3].id, departments[3].id   # 物理系的专业
        ]

        majors = []

        for i, code in enumerate(major_codes):
            major = Major.query.filter_by(major_code=code).first()
            if not major:
                major = Major(
                    major_code=code, 
                    major_name=major_names[i], 
                    dept_id=major_dept_ids[i]
                )
                majors.append(major)
                print(f"创建专业: {major_names[i]}")
            else:
                majors.append(major)
                print(f"专业已存在: {major_names[i]}")

        # 添加到数据库
        for major in majors:
            if not major.id:
                db.session.add(major)

        db.session.commit()

        print("院系和专业数据初始化完成！")

if __name__ == "__main__":
    init_departments_and_majors()
