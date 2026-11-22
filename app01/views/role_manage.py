"""
角色管理视图（RBAC）
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from app01.models import Role
from app01.forms import RoleModelForm


def role_list(request):
    """角色列表：预取权限，并统计已分配用户数"""
    queryset = Role.objects.all().prefetch_related("permissions").order_by("id")
    role_user_counts = {
        role.id: role.user_set.count() for role in queryset
    }
    return render(request, "app01/role_list.html", {
        "role_list": queryset,
        "role_user_counts": role_user_counts,
    })


def role_add(request):
    """新建角色"""
    if request.method == "GET":
        form = RoleModelForm()
        return render(request, "app01/role_change.html", {"form": form})

    form = RoleModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, "角色创建成功")
        return redirect("/role/list/")
    return render(request, "app01/role_change.html", {"form": form})


def role_edit(request, pk):
    """编辑角色（分配权限）"""
    role = Role.objects.filter(id=pk).first()
    if not role:
        messages.error(request, "角色不存在或已被删除")
        return redirect("/role/list/")

    if request.method == "GET":
        form = RoleModelForm(instance=role)
        return render(request, "app01/role_change.html", {"form": form})

    form = RoleModelForm(data=request.POST, instance=role)
    if form.is_valid():
        form.save()
        messages.success(request, f"角色「{role.title}」权限已更新")
        return redirect("/role/list/")
    return render(request, "app01/role_change.html", {"form": form})


def role_delete(request, pk):
    """删除角色：已分配给用户的角色禁止删除"""
    role = Role.objects.filter(id=pk).first()
    if not role:
        messages.error(request, "角色不存在或已被删除")
        return redirect("/role/list/")

    user_count = role.user_set.count()
    if user_count > 0:
        messages.error(request, f"角色「{role.title}」已分配给 {user_count} 名用户，请先调整用户角色后再删除")
        return redirect("/role/list/")

    role.delete()
    messages.success(request, f"角色「{role.title}」已删除")
    return redirect("/role/list/")
