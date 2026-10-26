from django.shortcuts import render, redirect
from app01.models import UserInfo, Department
from app01.utils.form import UserModelForm


def user_add(request):
    """添加用户（原始方式）"""
    if request.method == "GET":
        context = {
            "gender_choices": UserInfo.gender_choices,
            "depart_list": Department.objects.all(),
        }
        return render(request, "user_add.html", context)

    # 获取用户提交的数据
    user = request.POST.get("user", "").strip()
    pwd = request.POST.get("pwd", "").strip()
    age = request.POST.get("age", "").strip()
    account = request.POST.get("ac", "").strip()
    ctime = request.POST.get("ctime", "").strip()
    gender = request.POST.get("gd", "").strip()
    depart_id = request.POST.get("dp", "").strip()

    # 简单校验：任一必填项为空则返回错误提示
    if not all([user, pwd, age, account, ctime, gender, depart_id]):
        context = {
            "gender_choices": UserInfo.gender_choices,
            "depart_list": Department.objects.all(),
            "error": "请完整填写所有字段",
            "data": request.POST,
        }
        return render(request, "user_add.html", context)

    # 添加到数据库中
    UserInfo.objects.create(name=user, password=pwd, age=age,
                            account=account, create_time=ctime,
                            gender=gender, depart_id=depart_id)

    # 返回到用户列表页面
    return redirect("/user/list/")


def user_delete(request):
    """删除用户（对应 user_list.html 中的 ?nid= 链接）"""
    nid = request.GET.get("nid")
    UserInfo.objects.filter(id=nid).delete()
    return redirect("/user/list/")


def user_model_form_add(request):
    """添加用户（ModelForm版本）"""
    if request.method == "GET":
        form = UserModelForm()
        return render(request, "user_model_form_add.html", {"form": form})

    # 用户POST提交数据，数据校验，拿到 request.POST 的所有数据逐个字段校验
    form = UserModelForm(data=request.POST)
    if form.is_valid():
        # 如果数据合法，保存到数据库
        # {'name': '123', 'password': '123', 'age': 11, 'account': Decimal('0'), ...}
        # print(form.cleaned_data)

        # 代替之前的 models.UserInfo.objects.create(...)
        form.save()
        return redirect("/user/list/")

    # 校验失败（在页面上显示错误信息）form 从空到有数据到加入错误数据，错误提示
    # 不仅能展示错误信息还能保留原来你填过的数据
    return render(request, "user_model_form_add.html", {"form": form})


def user_list(request):
    """用户列表"""
    queryset = UserInfo.objects.all().order_by("-id")
    return render(request, "user_list.html", {"queryset": queryset})


def user_edit(request, nid):
    """编辑用户"""
    # 根据id获取某一行对象
    row_object = UserInfo.objects.filter(id=nid).first()

    if request.method == "GET":
        # 根据ID去数据库获取要编辑的那一行数据（对象）显示在输入框中
        form = UserModelForm(instance=row_object)
        return render(request, template_name='user_edit.html', context={'form': form})

    # instance=row_object这里是代表更新到某一行，不然form.save()会单独加一条数据
    form = UserModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        # 默认保存的是用户输入的所有数据，如果想要再用户输入以外增加一点值
        # form.instance.字段名 = 值
        form.save()
        return redirect('/user/list/')
    return render(request, template_name='user_edit.html', context={"form": form})
