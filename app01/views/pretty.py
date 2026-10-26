from django.shortcuts import render, redirect, HttpResponse
from app01.models import PrettyNum
from app01.utils.pagination import Pagination
import re


def pretty_list(request):
    """靓号列表（支持搜索 + 分页）"""
    keyword = request.GET.get("keyword", "").strip()
    queryset = PrettyNum.objects.all().order_by("-level")
    if keyword:
        queryset = queryset.filter(mobile__contains=keyword)

    pager = Pagination(request, queryset, page_size=10)
    return render(request, "pretty_list.html", {
        "pretty_list": pager.page_queryset,
        "page_string": pager.html(),
        "keyword": keyword,
    })


def _check_pretty_data(mobile, price, level, status):
    """校验靓号表单数据，返回错误字典（无错误时为空）"""
    error = {}
    # 手机号严格校验：以 1 开头，第二位 3~9，共 11 位（真实手机号格式）
    if not re.fullmatch(r"1[3-9]\d{9}", mobile):
        error["mobile"] = "手机号格式错误"
    if not price or not price.isdecimal():
        error["price"] = "价格必须是非负整数"
    if level not in ("1", "2", "3", "4"):
        error["level"] = "级别必须是 1~4 级"
    if status not in ("1", "2"):
        error["status"] = "状态选择不正确"
    return error


def pretty_add(request):
    """新建靓号"""
    if request.method == "GET":
        return render(request, "pretty_add.html")

    mobile = request.POST.get("mobile", "").strip()
    price = request.POST.get("price", "").strip()
    level = request.POST.get("level", "").strip()
    status = request.POST.get("status", "").strip()

    error = _check_pretty_data(mobile, price, level, status)
    if not error and PrettyNum.objects.filter(mobile=mobile).exists():
        error["mobile"] = "该手机号已存在"

    if error:
        return render(request, "pretty_add.html", {"error": error, "data": request.POST})

    PrettyNum.objects.create(mobile=mobile, price=int(price), level=int(level), status=int(status))
    return redirect("/pretty/list/")


def pretty_edit(request, nid):
    """编辑靓号"""
    row_object = PrettyNum.objects.filter(id=nid).first()
    if not row_object:
        return HttpResponse("靓号不存在")

    if request.method == "GET":
        return render(request, "pretty_edit.html", {"pretty": row_object})

    mobile = request.POST.get("mobile", "").strip()
    price = request.POST.get("price", "").strip()
    level = request.POST.get("level", "").strip()
    status = request.POST.get("status", "").strip()

    error = _check_pretty_data(mobile, price, level, status)
    if not error and PrettyNum.objects.filter(mobile=mobile).exclude(id=nid).exists():
        error["mobile"] = "该手机号已存在"

    if error:
        return render(request, "pretty_edit.html", {"pretty": row_object, "error": error, "data": request.POST})

    PrettyNum.objects.filter(id=nid).update(mobile=mobile, price=int(price), level=int(level), status=int(status))
    return redirect("/pretty/list/")


def pretty_delete(request, nid):
    """删除靓号"""
    PrettyNum.objects.filter(id=nid).delete()
    return redirect("/pretty/list/")
