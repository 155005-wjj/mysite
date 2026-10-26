from django.shortcuts import render, redirect, HttpResponse
from app01.models import Department


def depart_list(request):
    """部门列表"""
    # 去数据库获取所有部门
    queryset = Department.objects.all().order_by("id")
    return render(request, "depart_list1.html", {"queryset": queryset})


def depart_add(request):
    """添加部门"""
    if request.method == "GET":
        return render(request, "depart_add1.html")

    # POST：拿到用户提交的部门名称并入库
    title = request.POST.get("title", "").strip()
    if not title:
        return render(request, "depart_add1.html", {"error": "部门名称不能为空"})
    Department.objects.create(title=title)
    return redirect("/depart/list/")


def depart_edit(request, nid):
    """编辑部门"""
    row_object = Department.objects.filter(id=nid).first()
    if not row_object:
        return HttpResponse("部门不存在")

    if request.method == "GET":
        return render(request, "depart_edit1.html", {"row_object": row_object})

    title = request.POST.get("title", "").strip()
    if not title:
        return render(request, "depart_edit1.html", {"row_object": row_object, "error": "部门名称不能为空"})
    Department.objects.filter(id=nid).update(title=title)
    return redirect("/depart/list/")


def depart_delete(request):
    """删除部门"""
    nid = request.GET.get("nid")
    Department.objects.filter(id=nid).delete()
    return redirect("/depart/list/")
