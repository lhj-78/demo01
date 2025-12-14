
// 测试院系和专业关联功能
document.addEventListener('DOMContentLoaded', function() {
    console.log('测试页面已加载');

    const departmentSelect = document.getElementById('department_id');
    const majorSelect = document.getElementById('major_id');

    if (!departmentSelect || !majorSelect) {
        console.error('找不到院系或专业下拉框');
        return;
    }

    // 加载专业列表的函数
    function loadMajors(departmentId) {
        console.log('加载专业列表，院系ID:', departmentId);

        // 清空专业下拉框
        majorSelect.innerHTML = '';

        if (departmentId == 0) {
            // 如果没有选择院系，显示提示信息
            const option = document.createElement('option');
            option.value = 0;
            option.textContent = '请先选择院系';
            majorSelect.appendChild(option);
            return;
        }

        // 发送AJAX请求获取该院系下的专业
        fetch(`/api/majors/${departmentId}`)
            .then(response => {
                console.log('API响应状态:', response.status);
                return response.json();
            })
            .then(data => {
                console.log('API返回的数据:', data);

                // 添加默认选项
                const defaultOption = document.createElement('option');
                defaultOption.value = 0;
                defaultOption.textContent = '请选择专业';
                majorSelect.appendChild(defaultOption);

                // 添加专业选项
                data.forEach(major => {
                    const option = document.createElement('option');
                    option.value = major.id;
                    option.textContent = major.major_name;
                    majorSelect.appendChild(option);
                });
            })
            .catch(error => {
                console.error('获取专业列表失败:', error);
                const option = document.createElement('option');
                option.value = 0;
                option.textContent = '获取专业列表失败';
                majorSelect.appendChild(option);
            });
    }

    // 当院系选择改变时，更新专业下拉框
    departmentSelect.addEventListener('change', function() {
        console.log('院系选择已改变:', this.value);
        loadMajors(this.value);
    });

    // 页面加载时，如果已选择院系，则加载对应的专业列表
    if (departmentSelect.value > 0) {
        console.log('页面加载时已选择院系:', departmentSelect.value);
        loadMajors(departmentSelect.value);
    } else if (departmentSelect.options.length > 1) {
        // 如果没有选择院系，但有院系选项，则自动选择第一个院系
        console.log('自动选择第一个院系');
        departmentSelect.value = departmentSelect.options[1].value;
        loadMajors(departmentSelect.value);
    }

    // 添加一个全局函数，以便在HTML中调用
    window.loadMajors = loadMajors;
});
