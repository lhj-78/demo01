
from app import app, db
from models import Department, Major

def init_majors():
    """初始化专业数据"""
    with app.app_context():
        # 检查院系数据
        departments = Department.query.all()
        print(f"当前院系数量: {len(departments)}")

        # 检查专业数据
        majors = Major.query.all()
        print(f"当前专业数量: {len(majors)}")

        # 如果没有院系数据，则创建
        if len(departments) == 0:
            print("创建院系数据...")
            dept1 = Department(dept_code='CS', dept_name='计算机科学系', dean='张教授', office_location='信息楼A101', phone='12345678')
            dept2 = Department(dept_code='EE', dept_name='电子工程系', dean='李教授', office_location='工程楼B201', phone='87654321')
            dept3 = Department(dept_code='MA', dept_name='数学系', dean='王教授', office_location='理学楼C301', phone='11223344')
            dept4 = Department(dept_code='PH', dept_name='物理系', dean='赵教授', office_location='理学楼D401', phone='55667788')

            db.session.add(dept1)
            db.session.add(dept2)
            db.session.add(dept3)
            db.session.add(dept4)
            db.session.commit()
            print("院系数据创建完成")

            # 重新获取院系数据
            departments = Department.query.all()

        # 如果没有专业数据，则创建
        if len(majors) == 0:
            print("创建专业数据...")
            # 计算机科学系的专业
            cs_dept = Department.query.filter_by(dept_code='CS').first()
            cs_major1 = Major(major_code='CS01', major_name='计算机科学与技术', dept_id=cs_dept.id)
            cs_major2 = Major(major_code='CS02', major_name='软件工程', dept_id=cs_dept.id)
            cs_major3 = Major(major_code='CS03', major_name='人工智能', dept_id=cs_dept.id)

            # 电子工程系的专业
            ee_dept = Department.query.filter_by(dept_code='EE').first()
            ee_major1 = Major(major_code='EE01', major_name='电子信息工程', dept_id=ee_dept.id)
            ee_major2 = Major(major_code='EE02', major_name='通信工程', dept_id=ee_dept.id)

            # 数学系的专业
            ma_dept = Department.query.filter_by(dept_code='MA').first()
            ma_major1 = Major(major_code='MA01', major_name='基础数学', dept_id=ma_dept.id)
            ma_major2 = Major(major_code='MA02', major_name='应用数学', dept_id=ma_dept.id)

            # 物理系的专业
            ph_dept = Department.query.filter_by(dept_code='PH').first()
            ph_major1 = Major(major_code='PH01', major_name='理论物理', dept_id=ph_dept.id)
            ph_major2 = Major(major_code='PH02', major_name='应用物理', dept_id=ph_dept.id)

            # 添加到数据库
            db.session.add(cs_major1)
            db.session.add(cs_major2)
            db.session.add(cs_major3)
            db.session.add(ee_major1)
            db.session.add(ee_major2)
            db.session.add(ma_major1)
            db.session.add(ma_major2)
            db.session.add(ph_major1)
            db.session.add(ph_major2)

            db.session.commit()
            print("专业数据创建完成")

        # 打印所有院系和专业数据
        print("\n院系和专业数据:")
        for dept in departments:
            majors_in_dept = Major.query.filter_by(dept_id=dept.id).all()
            print(f"院系: {dept.dept_name} (ID: {dept.id}) - 专业数量: {len(majors_in_dept)}")
            for major in majors_in_dept:
                print(f"  - {major.major_name} (ID: {major.id})")

if __name__ == "__main__":
    init_majors()
