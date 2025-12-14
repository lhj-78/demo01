
from app import app, db
from models import Course, Major

def check_courses():
    """查看数据库中的课程信息"""
    with app.app_context():
        # 查询所有课程
        courses = Course.query.all()
        print("当前数据库中的课程:")
        for course in courses:
            major_name = course.major.major_name if course.major else "未关联专业"
            print(f"ID: {course.id}, 课程代码: {course.course_code}, 课程名称: {course.course_name}, 学分: {course.credit}, 所属专业: {major_name}")

        # 查询所有专业
        majors = Major.query.all()
        print("\n当前数据库中的专业:")
        for major in majors:
            print(f"ID: {major.id}, 专业代码: {major.major_code}, 专业名称: {major.major_name}")

if __name__ == "__main__":
    check_courses()
