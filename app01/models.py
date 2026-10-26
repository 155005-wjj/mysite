from django.db import models


class Department(models.Model):
    """ 部门表 """
    # verbose_name：Django 后台/表单中显示的字段名；max_length 限制最大长度
    title = models.CharField(verbose_name="部门名称", max_length=32)

    def __str__(self):
        # 让对象在后台/下拉框中显示为部门名称而不是 "Department object"
        return self.title


class UserInfo(models.Model):
    """ 员工表 """
    name = models.CharField(verbose_name="姓名", max_length=16)
    password = models.CharField(verbose_name="密码", max_length=64)
    age = models.IntegerField(verbose_name="年龄")
    # DecimalField：精确小数类型，适合金额；max_digits 总位数，decimal_places 小数位数
    account = models.DecimalField(verbose_name="账户余额", max_digits=10, decimal_places=2, default=0)
    # create_time = models.DateTimeField(verbose_name="入职时间")   # 包含时分秒
    create_time = models.DateField(verbose_name="入职时间")
    # 外键：关联部门表（一对多，一个部门下有多名员工）
    # to_field="id" 关联部门主键；on_delete=models.CASCADE 部门删除时员工一并删除
    depart = models.ForeignKey(to="Department", to_field="id", on_delete=models.CASCADE)
    # choices：限定字段可选值，数据库中存数字(1/2)，页面上显示对应的中文
    gender_choices = (
        (1, "男"),
        (2, "女"),
    )
    gender = models.SmallIntegerField(verbose_name="性别", choices=gender_choices)

    def __str__(self):
        return self.name


class Admin(models.Model):
    """ 管理员表 """
    username = models.CharField(verbose_name="用户名", max_length=32)
    password = models.CharField(verbose_name="密码", max_length=64)

    def __str__(self):
        return self.username


class PrettyNum(models.Model):
    """ 靓号表（特殊手机号） """
    mobile = models.CharField(verbose_name="手机号", max_length=11)
    # 想要允许为空 null=True, blank=True
    price = models.IntegerField(verbose_name="价格", default=0)
    level_choices = (
        (1, "1级"),
        (2, "2级"),
        (3, "3级"),
        (4, "4级"),
    )
    level = models.SmallIntegerField(verbose_name="级别", choices=level_choices, default=1)
    status_choices = (
        (1, "已占用"),
        (2, "未使用"),
    )
    status = models.SmallIntegerField(verbose_name="状态", choices=status_choices, default=2)

    def __str__(self):
        return self.mobile
