"""
数据智能点评（任务书 T4）
- 读取现有考勤 / 薪资数据，转为文本后注入提示词；
- 针对某员工某月数据，输出一句合理点评或改进建议。
"""
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from app01.models import Employee, Attendance, Salary
from app01.utils.ai import llm_client
from app01.utils.validators import sanitize_input


REVIEW_SYSTEM_PROMPT = """【角色】
你是企业人力资源分析助手，擅长根据员工的考勤与薪资数据给出客观点评。

【要求】
1. 只依据下面提供的该员工当月数据进行分析，不臆测未给出的信息。
2. 点评要客观、温和、具体，先总结表现，再给出 1~2 条可执行的改进建议。
3. 语言简洁，控制在 150 字以内，不要输出表格或数据明细。

【输出格式】
先一段“点评”，再一行“建议：……”。
"""


def _build_data_text(employee, month):
    """把员工指定月份的考勤、薪资数据汇总为纯文本，供注入提示词。"""
    attendances = Attendance.objects.filter(
        employee=employee, date__year=month[:4], date__month=int(month[5:7])
    ).order_by("date")
    salaries = Salary.objects.filter(employee=employee, month=month)

    lines = [
        f"员工姓名：{employee.name}",
        f"所属部门：{employee.depart.title if employee.depart else '未知'}",
        f"统计月份：{month}",
    ]

    # 考勤汇总
    status_map = dict(Attendance.STATUS_CHOICES)
    total = attendances.count()
    if total:
        counts = {1: 0, 2: 0, 3: 0, 4: 0}
        for att in attendances:
            counts[att.status] += 1
        lines.append(
            f"考勤记录共 {total} 天：按时 {counts[1]} 天，迟到 {counts[2]} 天，"
            f"早退 {counts[3]} 天，缺勤 {counts[4]} 天。"
        )
        for att in attendances:
            lines.append(
                f"- {att.date}：{status_map.get(att.status, att.status)}"
                f"（上班 {att.check_in or '无'}，下班 {att.check_out or '无'}）"
            )
    else:
        lines.append("考勤记录：本月暂无考勤数据。")

    # 薪资汇总
    for sal in salaries:
        lines.append(
            f"薪资：基本工资 {sal.base_salary} 元，奖金 {sal.bonus} 元，"
            f"扣款 {sal.deduction} 元，实发 {sal.total} 元。"
        )
    if not salaries:
        lines.append("薪资：本月暂无薪资数据。")

    return "\n".join(lines)


def review_page(request):
    """数据点评页面：传入员工列表与可选月份供下拉选择"""
    employees = Employee.objects.all().select_related("depart").order_by("id")
    months = Salary.objects.values_list("month", flat=True).distinct().order_by("month")
    return render(request, "app01/ai_review.html", {
        "employee_list": employees,
        "month_list": months,
    })


@csrf_exempt
def review_analyze(request):
    """AJAX：对指定员工指定月份做智能点评"""
    if request.method != "POST":
        return JsonResponse({"status": False, "msg": "请求方式错误"})

    employee_id = request.POST.get("employee_id", "")
    month = request.POST.get("month", "").strip()

    ok, month, error = sanitize_input(month, max_length=7)
    if not ok:
        return JsonResponse({"status": False, "msg": error})
    if not employee_id.isdigit():
        return JsonResponse({"status": False, "msg": "请选择员工"})

    employee = Employee.objects.filter(id=employee_id).first()
    if not employee:
        return JsonResponse({"status": False, "msg": "员工不存在"})

    data_text = _build_data_text(employee, month)
    prompt = f"请根据以下员工数据给出点评和建议：\n{data_text}"
    answer = llm_client.chat(prompt=prompt, system_prompt=REVIEW_SYSTEM_PROMPT)

    return JsonResponse({"status": True, "review": answer, "data_text": data_text})
