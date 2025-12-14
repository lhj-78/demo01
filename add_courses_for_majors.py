
from app import app, db
from models import Course, Major

def add_courses_for_majors():
    """为每个专业添加2-4个相关课程"""
    with app.app_context():
        # 查询所有专业
        majors = Major.query.all()

        # 为每个专业定义相关课程
        major_courses = {
            # 计算机科学系
            "计算机科学与技术": [
                {"course_code": "CS201", "course_name": "操作系统", "credit": 4.0, "description": "计算机操作系统的原理与实现"},
                {"course_code": "CS202", "course_name": "计算机网络", "credit": 3.5, "description": "计算机网络原理与技术"},
                {"course_code": "CS203", "course_name": "数据库系统", "credit": 3.0, "description": "数据库设计与管理"},
                {"course_code": "CS204", "course_name": "算法设计与分析", "credit": 4.0, "description": "算法设计与复杂度分析"}
            ],
            "软件工程": [
                {"course_code": "SE101", "course_name": "软件工程导论", "credit": 3.0, "description": "软件工程基本概念与方法"},
                {"course_code": "SE102", "course_name": "软件测试", "credit": 3.0, "description": "软件测试方法与工具"},
                {"course_code": "SE103", "course_name": "项目管理", "credit": 2.5, "description": "软件开发项目管理"},
                {"course_code": "SE104", "course_name": "软件架构设计", "credit": 3.5, "description": "大型软件系统架构设计"}
            ],
            "人工智能": [
                {"course_code": "AI101", "course_name": "机器学习", "credit": 4.0, "description": "机器学习算法与应用"},
                {"course_code": "AI102", "course_name": "深度学习", "credit": 4.0, "description": "深度神经网络原理与实践"},
                {"course_code": "AI103", "course_name": "自然语言处理", "credit": 3.5, "description": "NLP技术与应用"},
                {"course_code": "AI104", "course_name": "计算机视觉", "credit": 3.5, "description": "图像处理与识别技术"}
            ],
            # 电子工程系
            "电子信息工程": [
                {"course_code": "EE201", "course_name": "数字信号处理", "credit": 3.5, "description": "数字信号处理原理与应用"},
                {"course_code": "EE202", "course_name": "微电子技术", "credit": 4.0, "description": "集成电路设计与制造"},
                {"course_code": "EE203", "course_name": "通信原理", "credit": 3.5, "description": "通信系统基本原理"},
                {"course_code": "EE204", "course_name": "嵌入式系统", "credit": 3.0, "description": "嵌入式系统设计与开发"}
            ],
            "通信工程": [
                {"course_code": "CE101", "course_name": "移动通信", "credit": 3.5, "description": "移动通信系统与技术"},
                {"course_code": "CE102", "course_name": "光纤通信", "credit": 3.0, "description": "光纤通信原理与系统"},
                {"course_code": "CE103", "course_name": "卫星通信", "credit": 3.0, "description": "卫星通信系统与技术"}
            ],
            # 数学系
            "基础数学": [
                {"course_code": "MA101", "course_name": "高等代数", "credit": 4.0, "description": "线性代数与多项式理论"},
                {"course_code": "MA102", "course_name": "数学分析", "credit": 5.0, "description": "实数理论与微积分"},
                {"course_code": "MA103", "course_name": "复变函数", "credit": 3.5, "description": "复数与复变函数理论"},
                {"course_code": "MA104", "course_name": "微分方程", "credit": 3.5, "description": "常微分方程与偏微分方程"}
            ],
            "应用数学": [
                {"course_code": "AM101", "course_name": "概率论与数理统计", "credit": 4.0, "description": "概率论基础与统计方法"},
                {"course_code": "AM102", "course_name": "数值分析", "credit": 3.5, "description": "数值计算方法与误差分析"},
                {"course_code": "AM103", "course_name": "运筹学", "credit": 3.0, "description": "优化理论与方法"}
            ],
            # 物理系
            "理论物理": [
                {"course_code": "TP101", "course_name": "量子力学", "credit": 4.0, "description": "量子力学基本原理与应用"},
                {"course_code": "TP102", "course_name": "电动力学", "credit": 3.5, "description": "电磁场理论与麦克斯韦方程"},
                {"course_code": "TP103", "course_name": "热力学与统计物理", "credit": 3.5, "description": "热力学定律与统计物理基础"},
                {"course_code": "TP104", "course_name": "广义相对论", "credit": 3.0, "description": "引力理论与时空几何"}
            ],
            "应用物理": [
                {"course_code": "AP101", "course_name": "固体物理", "credit": 3.5, "description": "晶体结构与电子理论"},
                {"course_code": "AP102", "course_name": "光学", "credit": 3.0, "description": "光的波动性与量子性"},
                {"course_code": "AP103", "course_name": "半导体物理", "credit": 3.5, "description": "半导体材料与器件物理"}
            ],
            # 其他专业
            "文化遗产": [
                {"course_code": "CH101", "course_name": "文物保护技术", "credit": 3.0, "description": "文物保护的理论与方法"},
                {"course_code": "CH102", "course_name": "考古学概论", "credit": 3.0, "description": "考古学基本理论与方法"},
                {"course_code": "CH103", "course_name": "博物馆学", "credit": 2.5, "description": "博物馆管理与展览设计"}
            ],
            "电气工程及其自动化": [
                {"course_code": "EA101", "course_name": "电力系统分析", "credit": 3.5, "description": "电力系统稳态与暂态分析"},
                {"course_code": "EA102", "course_name": "自动控制原理", "credit": 3.5, "description": "控制系统分析与设计"},
                {"course_code": "EA103", "course_name": "电机学", "credit": 3.0, "description": "电机原理与应用"},
                {"course_code": "EA104", "course_name": "电力电子技术", "credit": 3.0, "description": "电力电子变换器与控制"}
            ],
            "汉语言文学": [
                {"course_code": "CL101", "course_name": "古代文学", "credit": 3.0, "description": "中国古代文学作品选读"},
                {"course_code": "CL102", "course_name": "现代文学", "credit": 3.0, "description": "中国现代文学作品选读"},
                {"course_code": "CL103", "course_name": "文学理论", "credit": 3.0, "description": "文学理论与批评方法"},
                {"course_code": "CL104", "course_name": "语言学概论", "credit": 3.0, "description": "语言学基本理论与方法"}
            ]
        }

        # 为每个专业添加课程
        for major in majors:
            major_name = major.major_name
            if major_name in major_courses:
                print(f"为专业 '{major_name}' 添加课程...")
                for course_data in major_courses[major_name]:
                    # 检查课程是否已存在
                    existing_course = Course.query.filter_by(course_code=course_data["course_code"]).first()
                    if not existing_course:
                        # 创建新课程
                        new_course = Course(
                            course_code=course_data["course_code"],
                            course_name=course_data["course_name"],
                            credit=course_data["credit"],
                            description=course_data["description"],
                            major_id=major.id
                        )
                        db.session.add(new_course)
                        print(f"  添加课程: {course_data['course_code']} - {course_data['course_name']}")
                    else:
                        print(f"  课程已存在: {course_data['course_code']} - {course_data['course_name']}")

        # 提交更改
        db.session.commit()
        print("课程添加完成！")

if __name__ == "__main__":
    add_courses_for_majors()
