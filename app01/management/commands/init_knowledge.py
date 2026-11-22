"""
制度知识库初始化命令（预置考勤、报销、请假等条目，对应任务书 T3）
用法：python manage.py init_knowledge
"""
from django.core.management.base import BaseCommand
from app01.models import Knowledge


# 预置制度条目：标题 + 内容
KNOWLEDGE_DATA = [
    (
        "考勤打卡规定",
        "公司标准工作时间为周一至周五 9:00—18:00。员工应在 9:00 前完成上班打卡，"
        "18:00 后完成下班打卡。晚于 9:00 打卡记为迟到，早于 18:00 离岗记为早退，"
        "未打卡且未请假记为缺勤。每月迟到、早退累计 3 次及以上，计入当月绩效扣减。"
    ),
    (
        "加班与调休规定",
        "工作日加班需提前在系统中提交申请并经直属主管审批。工作日加班按 1.5 倍计发加班费，"
        "休息日加班优先安排调休，法定节假日加班按 3 倍计发加班费。加班时长以打卡记录为准。"
    ),
    (
        "费用报销规定",
        "员工因公产生的差旅费、交通费、业务招待费等可申请报销。报销须在费用发生后 15 个工作日内提交，"
        "附正规发票及消费明细，注明事由、参与人员。差旅费标准：市内交通据实报销，"
        "住宿标准每晚不超过 400 元，超标部分由个人承担。无正规发票的费用不予报销。"
    ),
    (
        "请假申请流程",
        "请假分为事假、病假、年假、婚假、产假等。请假须至少提前 1 天在系统提交申请，"
        "3 天以内由直属主管审批，3 天及以上需部门负责人审批。病假须附医院证明，"
        "年假按工龄核算：满 1 年享 5 天，满 10 年享 10 天，满 20 年享 15 天。"
        "未经审批擅自不到岗按缺勤处理。"
    ),
    (
        "薪资发放规定",
        "公司每月 15 日发放上月工资，遇节假日顺延。工资由基本工资、绩效奖金和各类补贴构成，"
        "并依法代扣社保、公积金及个人所得税。工资条可在薪资管理模块查询，"
        "对薪资有异议应在发放后 5 个工作日内向人事部提出复核。"
    ),
    (
        "试用期与转正规定",
        "新员工试用期一般为 3 个月（合同期限 1 年以上不满 3 年的为 2 个月）。"
        "试用期内考核合格者按期转正；考核不合格或不符合录用条件的，公司可依法解除劳动合同。"
        "转正后按正式员工标准享受各项福利。"
    ),
]


class Command(BaseCommand):
    help = "预置考勤、报销、请假等制度知识条目"

    def handle(self, *args, **options):
        for title, content in KNOWLEDGE_DATA:
            obj, created = Knowledge.objects.get_or_create(
                title=title, defaults={"content": content}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"制度条目《{title}》创建成功"))
            else:
                # 更新已有条目内容，保证资料为最新版本
                obj.content = content
                obj.save()
                self.stdout.write(self.style.WARNING(f"制度条目《{title}》已更新"))

        self.stdout.write(self.style.SUCCESS(
            f"制度知识库初始化完成，共 {Knowledge.objects.count()} 条"
        ))
