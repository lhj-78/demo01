
import sqlite3

def create_grade_table():
    # 创建数据库连接
    conn = sqlite3.connect("student_management.db")
    cursor = conn.cursor()

    # 创建grade表，允许score为NULL
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS grade (
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

    conn.commit()
    conn.close()
    print("创建了grade表，允许score为NULL")

if __name__ == "__main__":
    create_grade_table()
