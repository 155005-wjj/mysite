"""
BootStrap 表单样式混入

作用：给 ModelForm / Form 的每个字段自动补上 Bootstrap 的 form-control 样式，
避免在模板里逐个手写 class。文件上传类字段不能套 form-control，
用 bootstrap_exclude_fields 排除即可。
"""
from django import forms


class BootStrap:
    """表单样式混入类：统一给字段加 form-control 与 placeholder"""

    # 子类可覆盖：这些字段不套 form-control（如 FileField）
    bootstrap_exclude_fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name in self.bootstrap_exclude_fields:
                continue
            if field.widget.attrs:
                field.widget.attrs["class"] = "form-control"
                field.widget.attrs["placeholder"] = field.label
            else:
                field.widget.attrs = {
                    "class": "form-control",
                    "placeholder": field.label,
                }


class BootStrapForm(BootStrap, forms.Form):
    """带 Bootstrap 样式的普通表单"""


class BootStrapModelForm(BootStrap, forms.ModelForm):
    """带 Bootstrap 样式的 ModelForm"""
