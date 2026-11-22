"""
表单校验层
"""
import re
from django import forms
from app01.models import Employee, Task, Attendance, Salary, Notice, User, Role
from app01.utils.bootstrap import BootStrapModelForm


class EmployeeModelForm(forms.ModelForm):
    """员工表单（含姓名/年龄/手机号校验）"""

    class Meta:
        model = Employee
        fields = ["name", "age", "gender", "balance", "entry_date",
                  "mobile", "depart", "avatar"]
        widgets = {
            "entry_date": forms.DateInput(attrs={"type": "date"}),
        }

    def clean_name(self):
        # 姓名长度校验
        name = self.cleaned_data["name"]
        if len(name) < 2:
            raise forms.ValidationError("姓名至少2个字符")
        return name

    def clean_age(self):
        # 年龄范围校验
        age = self.cleaned_data["age"]
        if not (18 <= age <= 65):
            raise forms.ValidationError("年龄必须在18-65岁之间")
        return age

    def clean_mobile(self):
        # 手机号正则 + 唯一校验（编辑时排除自身）
        mobile = self.cleaned_data["mobile"]
        if not re.match(r"^1[3-9]\d{9}$", mobile):
            raise forms.ValidationError("手机号格式错误")
        queryset = Employee.objects.filter(mobile=mobile)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise forms.ValidationError("手机号已存在")
        return mobile


class AttendanceModelForm(forms.ModelForm):
    """考勤表单"""

    class Meta:
        model = Attendance
        fields = ["employee", "date", "check_in", "check_out"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "check_in": forms.TimeInput(attrs={"type": "time"}),
            "check_out": forms.TimeInput(attrs={"type": "time"}),
        }


class SalaryModelForm(forms.ModelForm):
    """薪资表单"""

    class Meta:
        model = Salary
        fields = ["employee", "month", "base_salary", "bonus", "deduction"]


class NoticeModelForm(forms.ModelForm):
    """公告表单"""

    class Meta:
        model = Notice
        fields = ["title", "content", "is_top"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 5}),
        }


class TaskModelForm(BootStrapModelForm):
    """任务表单（AJAX用），字段自动带 Bootstrap 样式"""

    class Meta:
        model = Task
        fields = ["level", "title", "detail", "leader"]
        widgets = {
            "detail": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_title(self):
        title = self.cleaned_data["title"]
        if len(title) < 2:
            raise forms.ValidationError("标题至少2个字符")
        return title


class UserModelForm(forms.ModelForm):
    """用户表单（不含密码）"""

    class Meta:
        model = User
        fields = ["username", "email", "is_superuser", "is_active", "roles"]


class RoleModelForm(forms.ModelForm):
    """角色表单"""

    class Meta:
        model = Role
        fields = ["title", "permissions"]
        widgets = {
            # 权限用复选框直接勾选，不用按住Ctrl
            "permissions": forms.CheckboxSelectMultiple()
        }
