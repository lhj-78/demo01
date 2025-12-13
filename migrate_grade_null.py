
import sqlite3
import os

def migrate_grade_null():
    # 备份当前数据库
    if os.path.exists("student_management.db"):
        os.rename("student_management.db", "student_management_backup.db")

    # 创建新的数据库连接
    conn = sqlite3.connect("student_management.db")
    cursor = conn.cursor()

    # 创建新的grade表，允许score为NULL
    cursor.execute("""
    CREATE TABLE grade (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        course_id INTEGER NOT NULL,
        score REAL,
        exam_date DATE,
        semester VARCHAR(20) NOT NULL,
        FOREIGN KEY (student_id) REFERENCES student (id),
        FOREIGN KEY (course_id) REFERENCES course (id)
    )
    """)

    # 从备份中复制数据
    backup_conn = sqlite3.connect("student_management_backup.db")
    backup_cursor = backup_conn.cursor()

    try:
        backup_cursor.execute("SELECT * FROM grade")
        grades = backup_cursor.fetchall()

        # 插入数据到新表
        for grade in grades:
            cursor.execute("""
            INSERT INTO grade (id, student_id, course_id, score, exam_date, semester)
            VALUES (?, ?, ?, ?, ?, ?)
            """, grade)

        conn.commit()
        print("数据库迁移成功完成！")
    except Exception as e:
        print(f"迁移过程中出错: {e}")
        conn.rollback()
    finally:
        backup_conn.close()
        conn.close()

if __name__ == "__main__":
    migrate_grade_null()
