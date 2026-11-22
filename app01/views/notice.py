"""
公告管理视图
"""
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from app01.models import Notice
from app01.forms import NoticeModelForm


def notice_list(request):
    """公告列表（搜索、分页、总数统计）"""
    keyword = request.GET.get("keyword", "").strip()
    queryset = Notice.objects.all().select_related("publisher")
    if keyword:
        queryset = queryset.filter(title__contains=keyword)

    total_count = queryset.count()
    paginator = Paginator(queryset, 8)
    page_obj = paginator.get_page(request.GET.get("page", 1))
    return render(request, "app01/notice_list.html", {
        "page_obj": page_obj, "keyword": keyword, "total_count": total_count
    })


def notice_add(request):
    """发布公告"""
    if request.method == "GET":
        form = NoticeModelForm()
        return render(request, "app01/notice_change.html", {"form": form})

    form = NoticeModelForm(data=request.POST)
    if form.is_valid():
        notice = form.save(commit=False)
        # 发布人取当前登录用户
        notice.publisher_id = request.session.get("user_id")
        notice.save()
        messages.success(request, "公告发布成功")
        return redirect("/notice/list/")
    return render(request, "app01/notice_change.html", {"form": form})


def notice_edit(request, pk):
    """编辑公告"""
    notice = Notice.objects.filter(id=pk).first()
    if not notice:
        messages.error(request, "公告不存在或已被删除")
        return redirect("/notice/list/")

    if request.method == "GET":
        form = NoticeModelForm(instance=notice)
        return render(request, "app01/notice_change.html", {"form": form})

    form = NoticeModelForm(data=request.POST, instance=notice)
    if form.is_valid():
        form.save()
        messages.success(request, "公告更新成功")
        return redirect("/notice/list/")
    return render(request, "app01/notice_change.html", {"form": form})


def notice_top(request, pk):
    """切换置顶状态"""
    notice = Notice.objects.filter(id=pk).first()
    if notice:
        notice.is_top = not notice.is_top
        notice.save()
    return redirect("/notice/list/")


def notice_delete(request, pk):
    """删除公告"""
    notice = Notice.objects.filter(id=pk).first()
    if not notice:
        return redirect("/notice/list/")
    notice.delete()
    messages.success(request, "公告已删除")
    return redirect("/notice/list/")
