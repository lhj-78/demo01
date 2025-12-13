
import sqlite3

def check_table_structure():
    conn = sqlite3.connect("student_management.db")
    cursor = conn.cursor()

    # 检查grade表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='grade'")
    table_exists = cursor.fetchone()

    if table_exists:
        print("grade表存在，表结构如下：")
        cursor.execute("PRAGMA table_info(grade)")
        columns = cursor.fetchall()
        for column in columns:
            print(f"  {column[1]}: {column[2]} {'NOT NULL' if column[3] else 'NULL'}")
    else:
        print("grade表不存在")

    conn.close()

if __name__ == "__main__":
    check_table_structure()
