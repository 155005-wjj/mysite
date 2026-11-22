"""
演示数据生成命令
用法：python manage.py demo_data
生成：三个标准角色、用户及角色分配、部门负责人、14个员工、考勤、薪资
"""
import datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from app01.models import (
    User, Department, Permission, Role, Employee, Attendance, Salary
)


def calc_status(check_in, check_out):
    """根据上下班时间自动计算考勤状态"""
    if not check_in:
        return 4
    if check_in > datetime.time(9, 0):
        return 2
    if check_out and check_out < datetime.time(18, 0):
        return 3
    return 1


# 6个登录用户（用户名、手机号、角色类型、负责部门）
# 6个全部=部门管理员
USER_DATA = [
    ("灭建国", "13312345681", "部门管理员", "技术部"),
    ("钢门", "13412345682", "部门管理员", "人事部"),
    ("小浣熊", "15012345683", "部门管理员", "财务部"),
    ("王俊杰", "15112345684", "部门管理员", "市场部"),
    ("毅神", "15212345685", "部门管理员", "运营部"),
    ("谢道驰", "15712345686", "部门管理员", "行政部"),
]

# 8个普通员工档案（姓名、年龄、性别、余额、入职时间、手机号、部门）
EMPLOYEE_DATA = [
    ("张伟", 32, 1, 8800, "2022-03-15", "13812345671", "技术部"),
    ("李芳", 29, 2, 6500, "2022-07-01", "13912345672", "人事部"),
    ("王强", 35, 1, 12000, "2021-01-20", "13712345673", "技术部"),
    ("刘洋", 41, 1, 15000, "2020-05-10", "13612345674", "财务部"),
    ("陈静", 26, 2, 5200, "2023-09-01", "13512345675", "市场部"),
    ("杨帆", 30, 1, 7800, "2022-11-11", "18812345676", "运营部"),
    ("赵磊", 38, 1, 9600, "2021-08-25", "18712345677", "行政部"),
    ("孙琳", 24, 2, 4500, "2024-02-18", "18612345678", "技术部"),
]

# 考勤5天的上下班时间模式（按时、迟到、早退、缺勤、按时）
ATTENDANCE_PATTERNS = [
    (datetime.time(8, 30), datetime.time(18, 30)),
    (datetime.time(9, 30), datetime.time(19, 0)),
    (datetime.time(8, 45), datetime.time(17, 30)),
    (None, None),
    (datetime.time(8, 50), datetime.time(18, 15)),
]

# 薪资三个月
SALARY_MONTHS = ["2026-09", "2026-10", "2026-11"]


class Command(BaseCommand):
    help = "生成角色、用户、员工、考勤、薪资演示数据"

    def handle(self, *args, **options):
        # ===== 1. 清理旧演示数据（保留粮食猪、部门、权限） =====
        Attendance.objects.all().delete()
        Salary.objects.all().delete()
        Employee.objects.all().delete()
        User.objects.exclude(username="粮食猪").delete()
        Role.objects.all().delete()
        self.stdout.write("已清理旧演示数据")

        dept_map = {d.title: d for d in Department.objects.all()}

        # ===== 2. 创建三个标准角色 =====
        # 超级管理员：全部权限
        super_role = Role.objects.create(title="超级管理员")
        super_role.permissions.set(Permission.objects.all())

        # 部门管理员：员工、考勤、薪资、公告、任务
        dept_role = Role.objects.create(title="部门管理员")
        dept_role.permissions.set(
            Permission.objects.filter(
                title__in=["员工管理", "考勤管理", "薪资管理", "公告管理", "任务管理"]
            )
        )

        # 普通员工：只有任务管理（工作）
        emp_role = Role.objects.create(title="普通员工")
        emp_role.permissions.set(
            Permission.objects.filter(title="任务管理")
        )
        self.stdout.write(self.style.SUCCESS("三个标准角色创建成功"))

        # ===== 3. 粮食猪分配超级管理员角色 =====
        liang = User.objects.get(username="粮食猪")
        liang.roles.set([super_role])
        self.stdout.write(self.style.SUCCESS("粮食猪 分配为 超级管理员"))

        # ===== 4. 创建6个用户，分配角色并设为部门负责人 =====
        for name, mobile, role_type, dept_name in USER_DATA:
            user = User.objects.create(username=name)
            user.set_password("123456")   # 安全哈希
            user.save()

            # 分配角色
            user.roles.set([dept_role if role_type == "部门管理员" else emp_role])

            # 设为对应部门负责人
            depart = dept_map[dept_name]
            depart.leader = user
            depart.save()
            self.stdout.write(self.style.SUCCESS(
                f"用户 {name} 创建，角色 {role_type}，{dept_name} 负责人"
            ))

        # ===== 5. 创建员工（6个登录用户 + 8个普通员工 = 14人，不含粮食猪） =====
        employees = []

        # 6个登录用户同时作为员工
        for name, mobile, role_type, dept_name in USER_DATA:
            emp = Employee.objects.create(
                name=name,
                age=36,
                gender=1,
                balance=Decimal("10000"),
                entry_date=datetime.date(2021, 6, 1),
                mobile=mobile,
                depart=dept_map[dept_name]
            )
            employees.append(emp)

        # 8个普通员工档案
        for name, age, gender, balance, entry, mobile, dept_name in EMPLOYEE_DATA:
            emp = Employee.objects.create(
                name=name,
                age=age,
                gender=gender,
                balance=Decimal(str(balance)),
                entry_date=datetime.datetime.strptime(entry, "%Y-%m-%d").date(),
                mobile=mobile,
                depart=dept_map[dept_name]
            )
            employees.append(emp)

        self.stdout.write(self.style.SUCCESS(
            f"员工创建完成，共 {Employee.objects.count()} 人（不含粮食猪）"
        ))

        # ===== 6. 生成考勤（每个员工5天，状态自动计算） =====
        base_date = datetime.date(2026, 10, 26)
        for emp in employees:
            for i, (check_in, check_out) in enumerate(ATTENDANCE_PATTERNS):
                Attendance.objects.create(
                    employee=emp,
                    date=base_date + datetime.timedelta(days=i),
                    check_in=check_in,
                    check_out=check_out,
                    status=calc_status(check_in, check_out)
                )
        self.stdout.write(self.style.SUCCESS(
            f"考勤记录生成完成，共 {Attendance.objects.count()} 条"
        ))

        # ===== 7. 生成薪资（每个员工3个月，实发自动计算） =====
        for idx, emp in enumerate(employees):
            base = Decimal(6000 + idx * 500)
            for m_idx, month in enumerate(SALARY_MONTHS):
                bonus = Decimal(800 + m_idx * 300)
                deduction = Decimal(200 if m_idx == 1 else 0)
                Salary.objects.create(
                    employee=emp,
                    month=month,
                    base_salary=base,
                    bonus=bonus,
                    deduction=deduction,
                    total=base + bonus - deduction
                )
        self.stdout.write(self.style.SUCCESS(
            f"薪资记录生成完成，共 {Salary.objects.count()} 条"
        ))

        self.stdout.write(self.style.SUCCESS("演示数据全部生成完成"))
