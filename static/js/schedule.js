// 课表视图切换功能
document.addEventListener('DOMContentLoaded', function() {
    // 获取视图切换按钮
    const weekViewBtn = document.getElementById('weekView');
    const listViewBtn = document.getElementById('listView');

    // 获取视图容器
    const weekViewContainer = document.getElementById('weekViewContainer');
    const listViewContainer = document.getElementById('listViewContainer');

    // 周视图按钮点击事件
    if (weekViewBtn) {
        weekViewBtn.addEventListener('click', function() {
            weekViewBtn.classList.remove('btn-outline-secondary');
            weekViewBtn.classList.add('btn-outline-primary');

            listViewBtn.classList.remove('btn-outline-primary');
            listViewBtn.classList.add('btn-outline-secondary');

            weekViewContainer.style.display = 'block';
            listViewContainer.style.display = 'none';
        });
    }

    // 列表视图按钮点击事件
    if (listViewBtn) {
        listViewBtn.addEventListener('click', function() {
            listViewBtn.classList.remove('btn-outline-secondary');
            listViewBtn.classList.add('btn-outline-primary');

            weekViewBtn.classList.remove('btn-outline-primary');
            weekViewBtn.classList.add('btn-outline-secondary');

            listViewContainer.style.display = 'block';
            weekViewContainer.style.display = 'none';
        });
    }

    // 为课程项添加点击事件，显示详细信息
    const courseItems = document.querySelectorAll('.course-item');
    courseItems.forEach(item => {
        item.style.cursor = 'pointer';
        item.addEventListener('click', function() {
            const courseName = this.querySelector('.course-name').textContent;
            const courseTeacher = this.querySelector('.course-teacher').textContent;
            const courseLocation = this.querySelector('.course-location').textContent;

            // 创建模态框显示课程详情
            const modal = new bootstrap.Modal(document.getElementById('courseDetailModal'));
            document.getElementById('modalCourseName').textContent = courseName;
            document.getElementById('modalCourseTeacher').textContent = courseTeacher;
            document.getElementById('modalCourseLocation').textContent = courseLocation;
            modal.show();
        });
    });
});