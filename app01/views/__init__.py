"""
视图模块统一导出
"""
# 认证
from .auth import login, logout, image_code
# 部门
from .department import (
    department_list, department_add,
    department_edit, department_delete, department_multi
)
# 员工
from .employee import (
    employee_list, employee_add,
    employee_edit, employee_delete
)
# 考勤
from .attendance import (
    attendance_list, attendance_add,
    attendance_edit, attendance_delete
)
# 薪资
from .salary import (
    salary_list, salary_add,
    salary_edit, salary_delete
)
# 公告
from .notice import (
    notice_list, notice_add, notice_edit,
    notice_top, notice_delete
)
# 任务（AJAX）
from .task import task_list, task_add_ajax, task_delete
# 数据统计
from .chart import (
    chart_index, chart_depart_people, chart_salary_trend
)
# 用户管理
from .user_manage import (
    user_list, user_add, user_edit,
    user_reset_pwd, user_delete
)
# 角色管理
from .role_manage import (
    role_list, role_add, role_edit, role_delete
)
# AI 智能助手
from .ai_jd import jd_page, jd_generate
from .ai_knowledge import knowledge_page, knowledge_ask
from .ai_review import review_page, review_analyze
from .ai_chat import (
    chat_page, chat_message, chat_stream, chat_clear,
    chat_save_key, chat_clear_key, chat_key_status
)
