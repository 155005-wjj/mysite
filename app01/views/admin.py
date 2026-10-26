from django.shortcuts import render
from app01.models import Admin


def admin_list(request):
    """管理员列表（仅页面样式，增删改查功能后续实现）"""
    keyword = request.GET.get("keyword", "").strip()
    queryset = Admin.objects.all()
    if keyword:
        queryset = queryset.filter(username__contains=keyword)

    return render(request, "admin_list.html", {
        "admin_list": queryset,
        "keyword": keyword,
    })
