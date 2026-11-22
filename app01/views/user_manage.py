"""
用户管理视图
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from app01.models import User, Role
from app01.forms import UserModelForm


def user_list(request):
    """用户列表：预取角色，消除 N+1"""
    queryset = User.objects.all().prefetch_related("roles").order_by("id")
    return render(request, "app01/user_manage_list.html", {"user_list": queryset})


def user_add(request):
    """新增用户"""
    if request.method == "GET":
        form = UserModelForm()
        return render(request, "app01/user_manage_change.html", {"form": form})

    form = UserModelForm(data=request.POST)
    if form.is_valid():
        user = form.save(commit=False)
        # 新增用户设置默认密码，用安全哈希
        user.set_password("123456")
        user.save()
        form.save_m2m()
        messages.success(request, f"用户「{user.username}」创建成功，初始密码 123456")
        return redirect("/user_manage/list/")
    return render(request, "app01/user_manage_change.html", {"form": form})


def user_edit(request, pk):
    """编辑用户（只改信息和角色，不改密码）"""
    user = User.objects.filter(id=pk).first()
    if not user:
        messages.error(request, "用户不存在或已被删除")
        return redirect("/user_manage/list/")

    if request.method == "GET":
        form = UserModelForm(instance=user)
        return render(request, "app01/user_manage_change.html", {"form": form})

    form = UserModelForm(data=request.POST, instance=user)
    if form.is_valid():
        form.save()
        messages.success(request, f"用户「{user.username}」信息已更新")
        return redirect("/user_manage/list/")
    return render(request, "app01/user_manage_change.html", {"form": form})


def user_reset_pwd(request, pk):
    """重置密码为 123456（不允许重置超级管理员）"""
    user = User.objects.filter(id=pk).first()
    if not user:
        messages.error(request, "用户不存在或已被删除")
        return redirect("/user_manage/list/")
    if user.is_superuser:
        messages.error(request, "超级管理员密码不允许在此重置")
        return redirect("/user_manage/list/")

    user.set_password("123456")
    user.save()
    messages.success(request, f"用户「{user.username}」密码已重置为 123456")
    return redirect("/user_manage/list/")


def user_delete(request, pk):
    """删除用户：禁止删除超级管理员、当前登录用户"""
    user = User.objects.filter(id=pk).first()
    if not user:
        messages.error(request, "用户不存在或已被删除")
        return redirect("/user_manage/list/")

    if user.is_superuser:
        messages.error(request, "超级管理员不允许删除")
        return redirect("/user_manage/list/")

    current_id = request.session.get("user_id")
    if current_id and int(pk) == int(current_id):
        messages.error(request, "不能删除当前登录的账号")
        return redirect("/user_manage/list/")

    user.delete()
    messages.success(request, f"用户「{user.username}」已删除")
    return redirect("/user_manage/list/")
