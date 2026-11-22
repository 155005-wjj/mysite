"""
薪资管理视图
"""
import re
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.contrib import messages
from app01.models import Salary, Employee
from app01.forms import SalaryModelForm

# 月份格式：YYYY-MM
MONTH_PATTERN = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


def _safe_int(value):
    if value is None or str(value).strip() == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def salary_list(request):
    """薪资列表（月份/员工筛选、总额统计、员工下拉）"""
    month = request.GET.get("month", "").strip()
    employee_id = _safe_int(request.GET.get("employee_id"))

    queryset = Salary.objects.all().select_related("employee")
    if month and MONTH_PATTERN.match(month):
        queryset = queryset.filter(month=month)
    if employee_id:
        queryset = queryset.filter(employee_id=employee_id)

    # 统计当前筛选结果的实发总额
    total_sum = queryset.aggregate(sum_total=Sum("total"))["sum_total"] or 0
    employee_list = Employee.objects.all().order_by("id")
    month_list = Salary.objects.values_list("month", flat=True).distinct().order_by("month")

    return render(request, "app01/salary_list.html", {
        "salary_list": queryset,
        "employee_list": employee_list,
        "month_list": month_list,
        "month": month,
        "employee_id": employee_id or "",
        "total_sum": total_sum,
    })


def salary_add(request):
    """新增薪资"""
    if request.method == "GET":
        form = SalaryModelForm()
        return render(request, "app01/salary_change.html", {"form": form})

    form = SalaryModelForm(data=request.POST)
    if form.is_valid():
        # commit=False 计算实发后再保存
        salary = form.save(commit=False)
        salary.total = salary.base_salary + salary.bonus - salary.deduction
        salary.save()
        messages.success(request, "薪资记录添加成功")
        return redirect("/salary/list/")
    return render(request, "app01/salary_change.html", {"form": form})


def salary_edit(request, pk):
    """编辑薪资"""
    salary = Salary.objects.filter(id=pk).first()
    if not salary:
        messages.error(request, "薪资记录不存在或已被删除")
        return redirect("/salary/list/")

    if request.method == "GET":
        form = SalaryModelForm(instance=salary)
        return render(request, "app01/salary_change.html", {"form": form})

    form = SalaryModelForm(data=request.POST, instance=salary)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.total = obj.base_salary + obj.bonus - obj.deduction
        obj.save()
        messages.success(request, "薪资记录更新成功")
        return redirect("/salary/list/")
    return render(request, "app01/salary_change.html", {"form": form})


def salary_delete(request, pk):
    """删除薪资"""
    salary = Salary.objects.filter(id=pk).first()
    if not salary:
        return redirect("/salary/list/")
    salary.delete()
    messages.success(request, "薪资记录已删除")
    return redirect("/salary/list/")
