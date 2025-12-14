
from app import app, db
from models import Department, Major

def check_data():
    with app.app_context():
        # 检查院系数据
        departments = Department.query.all()
        print(f"院系数量: {len(departments)}")
        for dept in departments:
            print(f"院系ID: {dept.id}, 代码: {dept.dept_code}, 名称: {dept.dept_name}")

        # 检查专业数据
        majors = Major.query.all()
        print(f"
专业数量: {len(majors)}")
        for major in majors:
            print(f"专业ID: {major.id}, 代码: {major.major_code}, 名称: {major.major_name}, 院系ID: {major.dept_id}")

        # 检查院系和专业的关联
        print("
院系与专业关联:")
        for dept in departments:
            majors_in_dept = Major.query.filter_by(dept_id=dept.id).all()
            print(f"院系: {dept.dept_name} - 专业数量: {len(majors_in_dept)}")
            for major in majors_in_dept:
                print(f"  - {major.major_name}")

if __name__ == "__main__":
    check_data()
