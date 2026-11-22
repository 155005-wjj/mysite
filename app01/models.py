"""
数据模型定义
"""
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """自定义用户模型（继承AbstractUser，密码用Django安全哈希）"""
    # 角色多对多
    roles = models.ManyToManyField("Role", verbose_name="角色", blank=True)

    class Meta:
        db_table = "sys_user"
        verbose_name = "用户"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


class Permission(models.Model):
    """权限模型"""
    title = models.CharField(verbose_name="权限名称", max_length=32)
    url = models.CharField(verbose_name="权限URL", max_length=128)

    class Meta:
        db_table = "sys_permission"
        verbose_name = "权限"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class Role(models.Model):
    """角色模型"""
    title = models.CharField(verbose_name="角色名称", max_length=32)
    permissions = models.ManyToManyField("Permission", verbose_name="权限", blank=True)

    class Meta:
        db_table = "sys_role"
        verbose_name = "角色"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class Department(models.Model):
    """部门模型"""
    title = models.CharField(verbose_name="部门名称", max_length=32)
    # 负责人关联用户，可空
    leader = models.ForeignKey(
        "User", verbose_name="负责人",
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name="lead_departments"
    )

    class Meta:
        db_table = "biz_department"
        verbose_name = "部门"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class Employee(models.Model):
    """员工模型"""
    GENDER_CHOICES = (
        (1, "男"),
        (2, "女"),
    )
    name = models.CharField(verbose_name="姓名", max_length=16)
    age = models.IntegerField(verbose_name="年龄")
    gender = models.SmallIntegerField(verbose_name="性别", choices=GENDER_CHOICES, default=1)
    balance = models.DecimalField(verbose_name="账户余额", max_digits=10, decimal_places=2, default=0)
    entry_date = models.DateField(verbose_name="入职时间")
    mobile = models.CharField(verbose_name="手机号", max_length=11, unique=True)
    depart = models.ForeignKey("Department", verbose_name="所属部门", on_delete=models.CASCADE)
    avatar = models.ImageField(verbose_name="头像", upload_to="avatar/", null=True, blank=True)

    class Meta:
        db_table = "biz_employee"
        verbose_name = "员工"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Attendance(models.Model):
    """考勤模型"""
    STATUS_CHOICES = (
        (1, "按时"),
        (2, "迟到"),
        (3, "早退"),
        (4, "缺勤"),
    )
    employee = models.ForeignKey("Employee", verbose_name="员工", on_delete=models.CASCADE)
    date = models.DateField(verbose_name="日期")
    check_in = models.TimeField(verbose_name="上班时间", null=True, blank=True)
    check_out = models.TimeField(verbose_name="下班时间", null=True, blank=True)
    status = models.SmallIntegerField(verbose_name="考勤状态", choices=STATUS_CHOICES, default=4)

    class Meta:
        db_table = "biz_attendance"
        verbose_name = "考勤"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.employee.name}-{self.date}"


class Salary(models.Model):
    """薪资模型"""
    employee = models.ForeignKey("Employee", verbose_name="员工", on_delete=models.CASCADE)
    month = models.CharField(verbose_name="月份", max_length=7)  # 格式：2026-11
    base_salary = models.DecimalField(verbose_name="基本工资", max_digits=10, decimal_places=2)
    bonus = models.DecimalField(verbose_name="奖金", max_digits=10, decimal_places=2, default=0)
    deduction = models.DecimalField(verbose_name="扣款", max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(verbose_name="实发工资", max_digits=10, decimal_places=2, default=0)

    class Meta:
        db_table = "biz_salary"
        verbose_name = "薪资"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.employee.name}-{self.month}"


class Notice(models.Model):
    """公告模型"""
    title = models.CharField(verbose_name="标题", max_length=64)
    content = models.TextField(verbose_name="内容")
    publisher = models.ForeignKey("User", verbose_name="发布人", on_delete=models.CASCADE)
    publish_time = models.DateTimeField(verbose_name="发布时间", auto_now_add=True)
    is_top = models.BooleanField(verbose_name="是否置顶", default=False)

    class Meta:
        db_table = "biz_notice"
        verbose_name = "公告"
        verbose_name_plural = verbose_name
        ordering = ["-is_top", "-publish_time"]

    def __str__(self):
        return self.title


class Knowledge(models.Model):
    """制度知识库条目（供 AI 问答检索注入，对应任务书 T3）"""
    title = models.CharField(verbose_name="标题", max_length=64)
    content = models.TextField(verbose_name="制度内容")

    class Meta:
        db_table = "biz_knowledge"
        verbose_name = "制度知识"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class Task(models.Model):
    """任务模型"""
    LEVEL_CHOICES = (
        (1, "紧急"),
        (2, "普通"),
        (3, "不急"),
    )
    level = models.SmallIntegerField(verbose_name="级别", choices=LEVEL_CHOICES, default=2)
    title = models.CharField(verbose_name="标题", max_length=64)
    detail = models.TextField(verbose_name="详情", blank=True)
    leader = models.ForeignKey("User", verbose_name="负责人", on_delete=models.CASCADE)

    class Meta:
        db_table = "biz_task"
        verbose_name = "任务"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title
