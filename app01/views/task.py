"""
任务管理视图（AJAX + 分页）

- 任务列表：左侧手写表单负责新建，右侧表格分页展示任务
- 新增走 AJAX，返回 JSON；校验失败按字段回显，成功后前端 location.reload() 刷新
- 表单校验统一复用 app01.forms.TaskModelForm（已接入 BootStrapModelForm）
"""
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from app01 import models
from app01.forms import TaskModelForm
from app01.utils.pagination import Pagination


def task_list(request):
    """任务列表页：分页数据 + 页码串 + 负责人下拉选项"""
    queryset = models.Task.objects.all().order_by("-id")
    page_object = Pagination(request, queryset, page_size=10)

    form = TaskModelForm()
    context = {
        "form": form,
        "queryset": page_object.page_queryset,  # 分完页的数据，只取当前页
        "page_string": page_object.html(),      # 生成的页码 HTML
        "leader_list": models.User.objects.all(),
    }
    return render(request, "app01/task_list.html", context)


@csrf_exempt
def task_add_ajax(request):
    """AJAX 新建任务：成功返回 status=True，失败按字段返回错误信息"""
    if request.method != "POST":
        return JsonResponse({"status": False, "msg": "请求方式错误"})

    form = TaskModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return JsonResponse({"status": True, "msg": "任务创建成功"})

    # 校验失败，收集错误信息返回（每个字段只取第一条提示）
    errors = {field: err_list[0] for field, err_list in form.errors.items()}
    return JsonResponse({"status": False, "errors": errors})


def task_delete(request, pk):
    """删除任务后回到列表页"""
    models.Task.objects.filter(id=pk).delete()
    return redirect("/task/list/")
