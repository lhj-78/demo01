
from app import app, db
from models import Student, Course
from sqlalchemy import text

def delete_student_course_table():
    """删除student_course关联表"""
    with app.app_context():
        try:
            # 获取所有学生
            students = Student.query.all()

            # 清空所有学生的课程关联
            for student in students:
                student.courses = []

            # 提交更改
            db.session.commit()

            # 删除关联表
            db.session.execute(text("DROP TABLE IF EXISTS student_course"))
            db.session.commit()

            print("student_course表已成功删除")
        except Exception as e:
            print(f"删除student_course表时出错: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    delete_student_course_table()
