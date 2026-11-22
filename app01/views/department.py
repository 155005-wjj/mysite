"""
部门管理视图
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Count
from openpyxl import load_workbook

from app01.models import Department, User, Employee


def department_list(request):
    """部门列表：带员工人数与负责人，消除 N+1 查询"""
    queryset = (
        Department.objects.all()
        .select_related("leader")
        .annotate(employee_count=Count("employee"))
        .order_by("id")
    )
    return render(request, "app01/department_list.html", {"depart_list": queryset})


def _clean_title(title):
    """部门标题清洗与长度校验"""
    title = (title or "").strip()
    if len(title) < 2:
        return None, "部门名称至少 2 个字符"
    if len(title) > 32:
        return None, "部门名称不能超过 32 个字符"
    return title, ""


def department_add(request):
    """新建部门"""
    if request.method == "GET":
        user_list = User.objects.all().order_by("id")
        return render(request, "app01/department_change.html", {"user_list": user_list})

    title, error = _clean_title(request.POST.get("title", ""))
    leader_id = request.POST.get("leader_id")
    if error:
        messages.error(request, error)
        user_list = User.objects.all().order_by("id")
        return render(request, "app01/department_change.html", {
            "user_list": user_list,
            "form_title": request.POST.get("title", ""),
            "leader_id": leader_id,
        })

    # 部门名称唯一校验
    if Department.objects.filter(title=title).exists():
        messages.error(request, f"部门「{title}」已存在")
        user_list = User.objects.all().order_by("id")
        return render(request, "app01/department_change.html", {
            "user_list": user_list,
            "form_title": title,
            "leader_id": leader_id,
        })

    Department.objects.create(
        title=title,
        leader_id=leader_id if leader_id else None
    )
    messages.success(request, f"部门「{title}」创建成功")
    return redirect("/depart/list/")


def department_edit(request, pk):
    """编辑部门"""
    depart = Department.objects.filter(id=pk).first()
    if not depart:
        messages.error(request, "部门不存在或已被删除")
        return redirect("/depart/list/")

    if request.method == "GET":
        user_list = User.objects.all().order_by("id")
        return render(request, "app01/department_change.html", {
            "depart": depart, "user_list": user_list
        })

    title, error = _clean_title(request.POST.get("title", ""))
    leader_id = request.POST.get("leader_id")
    if error:
        messages.error(request, error)
        user_list = User.objects.all().order_by("id")
        return render(request, "app01/department_change.html", {
            "depart": depart, "user_list": user_list,
            "leader_id": leader_id,
        })

    # 重名校验（排除自身）
    if Department.objects.filter(title=title).exclude(id=pk).exists():
        messages.error(request, f"部门「{title}」已存在")
        user_list = User.objects.all().order_by("id")
        return render(request, "app01/department_change.html", {
            "depart": depart, "user_list": user_list,
            "leader_id": leader_id,
        })

    depart.title = title
    depart.leader_id = leader_id if leader_id else None
    depart.save()
    messages.success(request, f"部门「{title}」更新成功")
    return redirect("/depart/list/")


def department_delete(request, pk):
    """删除部门：存在员工时禁止删除，避免员工成为无部门数据"""
    depart = Department.objects.filter(id=pk).first()
    if not depart:
        messages.error(request, "部门不存在或已被删除")
        return redirect("/depart/list/")

    employee_count = Employee.objects.filter(depart=depart).count()
    if employee_count > 0:
        messages.error(request, f"部门「{depart.title}」下还有 {employee_count} 名员工，请先调整员工归属后再删除")
        return redirect("/depart/list/")

    depart.delete()
    messages.success(request, f"部门「{depart.title}」已删除")
    return redirect("/depart/list/")


def department_multi(request):
    """
    批量导入部门（Excel）

    约定：Excel 第一个工作表，第一列写部门名称，从第 2 行开始（第 1 行为表头）。
    已存在的部门跳过，名称为空或长度不合规的行忽略。
    """
    file_object = request.FILES.get("exc")
    if not file_object:
        messages.error(request, "请先选择要上传的 Excel 文件")
        return redirect("/depart/list/")

    if not file_object.name.lower().endswith(".xlsx"):
        messages.error(request, "只支持 .xlsx 格式的 Excel 文件")
        return redirect("/depart/list/")

    try:
        # read_only=True 大文件也不会撑爆内存；只读第一个工作表
        wb = load_workbook(file_object, read_only=True)
        sheet = wb.worksheets[0]
    except Exception:
        messages.error(request, "文件解析失败，请确认上传的是有效的 Excel 文件")
        return redirect("/depart/list/")

    created_count = 0
    skip_count = 0
    invalid_count = 0

    try:
        # min_row=2 跳过表头，max_col=1 只读第一列
        for row in sheet.iter_rows(min_row=2, max_col=1, values_only=True):
            cell_value = row[0]
            if cell_value is None:
                continue

            title, error = _clean_title(str(cell_value))
            if error:
                invalid_count += 1
                continue

            # 部门名称去重：数据库无唯一约束，靠代码判断
            if Department.objects.filter(title=title).exists():
                skip_count += 1
                continue

            Department.objects.create(title=title)
            created_count += 1
    finally:
        wb.close()

    msg = f"导入完成：新增 {created_count} 个部门，跳过已存在 {skip_count} 个"
    if invalid_count:
        msg += f"，忽略无效行 {invalid_count} 个"
    messages.success(request, msg)
    return redirect("/depart/list/")
