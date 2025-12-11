
from app import app, db, User

def reset_admin_password():
    with app.app_context():
        # 查找管理员用户
        admin = User.query.filter_by(username='admin').first()

        if admin:
            # 重置密码为"admin123"
            admin.set_password("admin123")
            db.session.commit()
            print("管理员密码已重置为: admin123")
        else:
            print("未找到管理员用户")

if __name__ == "__main__":
    reset_admin_password()
