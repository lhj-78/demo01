
from app import app
from models import db, Course

# 在应用上下文中运行
with app.app_context():
    # 添加major_id列到Course表
    try:
        # 执行SQL语句添加列
        db.engine.execute('ALTER TABLE course ADD COLUMN major_id INTEGER')
        print("成功添加major_id列到course表")
    except Exception as e:
        print(f"添加列时出错: {e}")

    # 创建外键关系
    try:
        # 执行SQL语句创建外键关系
        db.engine.execute('CREATE INDEX idx_course_major_id ON course(major_id)')
        print("成功创建major_id索引")
    except Exception as e:
        print(f"创建索引时出错: {e}")
