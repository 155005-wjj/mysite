"""
员工管理视图
"""
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from app01.models import Employee, Department
from app01.forms import EmployeeModelForm


def _safe_int(value):
    """把 GET 参数安全转为整数，非法值返回 None"""
    if value is None or str(value).strip() == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def employee_list(request):
    """员工列表（搜索、部门筛选、分页、总数统计）"""
    keyword = request.GET.get("keyword", "").strip()
    depart_id = _safe_int(request.GET.get("depart_id"))

    # select_related 优化关联查询
    queryset = Employee.objects.all().select_related("depart")
    if keyword:
        queryset = queryset.filter(name__contains=keyword)
    if depart_id:
        queryset = queryset.filter(depart_id=depart_id)

    total_count = queryset.count()

    # 分页，每页8条
    paginator = Paginator(queryset, 8)
    page_obj = paginator.get_page(request.GET.get("page", 1))

    depart_list = Department.objects.all().order_by("id")
    return render(request, "app01/employee_list.html", {
        "page_obj": page_obj,
        "depart_list": depart_list,
        "keyword": keyword,
        "depart_id": depart_id or "",
        "total_count": total_count,
    })


def employee_add(request):
    """新建员工"""
    if request.method == "GET":
        form = EmployeeModelForm()
        return render(request, "app01/employee_change.html", {"form": form})

    # 带文件上传要用 request.FILES
    form = EmployeeModelForm(data=request.POST, files=request.FILES)
    if form.is_valid():
        form.save()
        return redirect("/employee/list/")
    return render(request, "app01/employee_change.html", {"form": form})


def employee_edit(request, pk):
    """编辑员工"""
    employee = Employee.objects.filter(id=pk).first()
    if not employee:
        return redirect("/employee/list/")

    if request.method == "GET":
        form = EmployeeModelForm(instance=employee)
        return render(request, "app01/employee_change.html", {"form": form})

    form = EmployeeModelForm(data=request.POST, files=request.FILES, instance=employee)
    if form.is_valid():
        form.save()
        return redirect("/employee/list/")
    return render(request, "app01/employee_change.html", {"form": form})


def employee_delete(request, pk):
    """删除员工"""
    employee = Employee.objects.filter(id=pk).first()
    if not employee:
        return redirect("/employee/list/")
    employee.delete()
    return redirect("/employee/list/")
