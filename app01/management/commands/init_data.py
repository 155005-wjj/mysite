"""
数据初始化命令：创建超级管理员、部门、权限、角色
用法：python manage.py init_data
"""
from django.core.management.base import BaseCommand
from app01.models import User, Department, Permission, Role


class Command(BaseCommand):
    help = "初始化超级管理员、部门、权限、角色数据"

    def handle(self, *args, **options):
        # 1. 创建超级管理员：粮食猪
        username = "粮食猪"
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f"用户 {username} 已存在，跳过创建"))
        else:
            User.objects.create_superuser(
                username=username,
                password="9178666",
                email=""
            )
            self.stdout.write(self.style.SUCCESS(f"超级管理员 {username} 创建成功"))

        # 2. 创建基础部门
        dept_names = ["技术部", "人事部", "财务部", "市场部", "运营部", "行政部"]
        for name in dept_names:
            _, created = Department.objects.get_or_create(title=name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"部门 {name} 创建成功"))

        # 3. 创建权限（对应各功能模块）
        perm_data = [
            ("部门管理", "/depart/list/"),
            ("员工管理", "/employee/list/"),
            ("考勤管理", "/attendance/list/"),
            ("薪资管理", "/salary/list/"),
            ("公告管理", "/notice/list/"),
            ("任务管理", "/task/list/"),
            ("数据统计", "/chart/"),
            ("用户管理", "/user_manage/list/"),
            ("角色管理", "/role/list/"),
        ]
        perm_objects = []
        for title, url in perm_data:
            perm, created = Permission.objects.get_or_create(title=title, url=url)
            perm_objects.append(perm)
            if created:
                self.stdout.write(self.style.SUCCESS(f"权限 {title} 创建成功"))

        # 4. 创建三个基础角色（对应任务书）
        # 超级管理员：拥有全部权限
        super_role, created = Role.objects.get_or_create(title="超级管理员")
        if created:
            super_role.permissions.set(perm_objects)
            self.stdout.write(self.style.SUCCESS("角色 超级管理员 创建成功（全部权限）"))

        # 部门管理员：员工、考勤、薪资、公告、任务
        dept_admin_role, created = Role.objects.get_or_create(title="部门管理员")
        if created:
            dept_perms = Permission.objects.filter(
                title__in=["员工管理", "考勤管理", "薪资管理", "公告管理", "任务管理"]
            )
            dept_admin_role.permissions.set(dept_perms)
            self.stdout.write(self.style.SUCCESS("角色 部门管理员 创建成功"))

        # 普通员工：公告、任务（只读相关）
        emp_role, created = Role.objects.get_or_create(title="普通员工")
        if created:
            emp_perms = Permission.objects.filter(title__in=["公告管理", "任务管理"])
            emp_role.permissions.set(emp_perms)
            self.stdout.write(self.style.SUCCESS("角色 普通员工 创建成功"))

        self.stdout.write(self.style.SUCCESS("数据初始化完成"))
