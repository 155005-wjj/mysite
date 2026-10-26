from django import forms


class BootstrapModelForm(forms.ModelForm):
    """统一为所有字段添加 Bootstrap 样式（form-control + placeholder）"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 循环找到所有的插件，添加了 class="form-control"
        for name, field in self.fields.items():
            # 如果其中某个字段不加样式
            # if name == "password":
            #     continue
            # placeholder="姓名" 样式也可以加
            field.widget.attrs = {"class": "form-control", "placeholder": field.label}
