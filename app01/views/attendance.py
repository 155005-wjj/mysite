"""
考勤管理视图
"""
import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from app01.models import Attendance, Employee
from app01.forms import AttendanceModelForm


def calc_status(check_in, check_out):
    """根据上下班时间自动计算考勤状态"""
    # 没有上班记录视为缺勤
    if not check_in:
        return 4
    # 晚于9:00上班算迟到
    if check_in > datetime.time(9, 0):
        return 2
    # 有下班记录且早于18:00算早退
    if check_out and check_out < datetime.time(18, 0):
        return 3
    # 其他情况按时
    return 1


def attendance_list(request):
    """考勤列表（员工筛选、状态统计）"""
    employee_id = request.GET.get("employee_id")
    try:
        employee_id = int(employee_id) if employee_id else None
    except (TypeError, ValueError):
        employee_id = None

    queryset = Attendance.objects.all().select_related("employee").order_by("-date", "id")
    if employee_id:
        queryset = queryset.filter(employee_id=employee_id)

    employee_list = Employee.objects.all().order_by("id")
    # 状态汇总：按时/迟到/早退/缺勤条数
    status_counts = {1: 0, 2: 0, 3: 0, 4: 0}
    for att in queryset:
        status_counts[att.status] = status_counts.get(att.status, 0) + 1

    return render(request, "app01/attendance_list.html", {
        "attendance_list": queryset,
        "employee_list": employee_list,
        "employee_id": employee_id or "",
        "status_counts": status_counts,
    })


def attendance_add(request):
    """新增考勤"""
    if request.method == "GET":
        form = AttendanceModelForm()
        return render(request, "app01/attendance_change.html", {"form": form})

    form = AttendanceModelForm(data=request.POST)
    if form.is_valid():
        # commit=False 先不写入数据库，计算状态后再保存
        attendance = form.save(commit=False)
        attendance.status = calc_status(attendance.check_in, attendance.check_out)
        attendance.save()
        messages.success(request, "考勤记录添加成功")
        return redirect("/attendance/list/")
    return render(request, "app01/attendance_change.html", {"form": form})


def attendance_edit(request, pk):
    """编辑考勤"""
    attendance = Attendance.objects.filter(id=pk).first()
    if not attendance:
        messages.error(request, "考勤记录不存在或已被删除")
        return redirect("/attendance/list/")

    if request.method == "GET":
        form = AttendanceModelForm(instance=attendance)
        return render(request, "app01/attendance_change.html", {"form": form})

    form = AttendanceModelForm(data=request.POST, instance=attendance)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.status = calc_status(obj.check_in, obj.check_out)
        obj.save()
        messages.success(request, "考勤记录更新成功")
        return redirect("/attendance/list/")
    return render(request, "app01/attendance_change.html", {"form": form})


def attendance_delete(request, pk):
    """删除考勤"""
    attendance = Attendance.objects.filter(id=pk).first()
    if not attendance:
        return redirect("/attendance/list/")
    attendance.delete()
    messages.success(request, "考勤记录已删除")
    return redirect("/attendance/list/")
