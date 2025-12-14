
// 院系专业联动功能
document.addEventListener('DOMContentLoaded', function() {
    console.log('注册页面已加载');

    // 获取院系和专业下拉框
    const departmentSelect = document.getElementById('department_id');
    const majorSelect = document.getElementById('major_id');

    console.log('院系下拉框:', departmentSelect);
    console.log('专业下拉框:', majorSelect);

    if (!departmentSelect || !majorSelect) {
        console.error('找不到院系或专业下拉框');
        return;
    }

    console.log('院系下拉框选项数量:', departmentSelect.options.length);
    for (let i = 0; i < departmentSelect.options.length; i++) {
        console.log(`选项 ${i}: 值=${departmentSelect.options[i].value}, 文本=${departmentSelect.options[i].text}`);
    }

    // 院系变化时更新专业列表
    departmentSelect.addEventListener('change', function() {
        const deptId = this.value;
        console.log('院系选择已改变:', deptId);
        console.log('发送请求到:', `/api/majors/${deptId}`);

        // 清空专业下拉框
        majorSelect.innerHTML = '<option value="0">请选择专业</option>';

        // 如果没有选择院系，直接返回
        if (!deptId || deptId === '0') {
            console.log('未选择院系，返回');
            return;
        }

        // 使用XMLHttpRequest发送AJAX请求获取专业列表
        const xhr = new XMLHttpRequest();
        xhr.open('GET', `/api/majors/${deptId}`, true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                console.log('响应状态:', xhr.status);
                console.log('响应文本:', xhr.responseText);

                if (xhr.status === 200) {
                    try {
                        // 确保响应文本不为空
                        if (!xhr.responseText || xhr.responseText.trim() === '') {
                            console.log('响应文本为空');
                            const noDataOption = document.createElement('option');
                            noDataOption.value = 0;
                            noDataOption.textContent = '没有专业数据';
                            majorSelect.appendChild(noDataOption);
                            return;
                        }

                        const data = JSON.parse(xhr.responseText);
                        console.log('获取的专业列表:', data);

                        // 添加专业选项
                        if (data && Array.isArray(data) && data.length > 0) {
                            data.forEach(major => {
                                console.log('添加专业:', major.major_name);
                                const option = document.createElement('option');
                                option.value = major.id;
                                option.textContent = major.major_name;
                                majorSelect.appendChild(option);
                            });
                        } else {
                            console.log('没有专业数据');
                            const option = document.createElement('option');
                            option.value = "0";
                            option.textContent = "该院系暂无专业";
                            majorSelect.appendChild(option);
                        }
                    } catch (e) {
                        console.error('JSON解析错误:', e);
                        console.error('响应文本:', xhr.responseText);
                        const option = document.createElement('option');
                        option.value = "0";
                        option.textContent = "数据解析失败";
                        majorSelect.appendChild(option);
                    }
                } else {
                    console.error('HTTP错误:', xhr.status);
                    console.error('响应文本:', xhr.responseText);
                    const option = document.createElement('option');
                    option.value = "0";
                    option.textContent = "获取专业列表失败";
                    majorSelect.appendChild(option);
                }
            }
        };
        xhr.send();
    });

    // 页面加载时，不自动选择院系，显示"请选择院系"
    console.log('页面加载时，院系选择值:', departmentSelect.value);
    // 确保院系下拉框选择第一个选项（"请选择院系"）
    departmentSelect.selectedIndex = 0;
    // 确保专业下拉框显示"请选择专业"
    majorSelect.innerHTML = '<option value="0">请选择专业</option>';
    console.log('页面加载完成，等待用户选择院系');
});
