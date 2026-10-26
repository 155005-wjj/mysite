from django import forms
from app01.models import Department, UserInfo
from app01.utils.bootstrap import BootstrapModelForm


class DepartmentModelForm(BootstrapModelForm):
    class Meta:
        model = Department
        fields = ["title"]


class UserModelForm(BootstrapModelForm):
    name = forms.CharField(min_length=3, label="用户名")
    # password = forms.CharField(label="密码", validators=[...])

    class Meta:
        model = UserInfo
        # fields 会生成输入框，gender 会自动获取字段变成下拉框
        # 但是这里 depart 获取的是对象，例如我们之前输出的类型
        fields = ["name", "password", "age", "account", "create_time", "depart", "gender"]

        # '''对应原来 <input type="text" class="form-control">
        # 中的 class="form-control" 的样式'''
        # widgets = {
        #     "name": forms.TextInput(attrs={"class": "form-control"}),
        #     "password": forms.PasswordInput(attrs={"class": "form-control"}),
        #     "age": forms.TextInput(attrs={"class": "form-control"}),
        # }
