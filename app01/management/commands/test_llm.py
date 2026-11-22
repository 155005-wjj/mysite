"""
大模型连通性测试命令
用法：python manage.py test_llm
说明：输入一句话，验证 LLMClient 能否正确返回模型回答（对应任务书 T1）。
"""
from django.core.management.base import BaseCommand
from app01.utils.ai import llm_client


class Command(BaseCommand):
    help = "测试大模型接口：输入一句话，输出模型回答"

    def add_arguments(self, parser):
        parser.add_argument(
            "message", nargs="?", default="你好，请用一句话介绍你自己。",
            help="发送给大模型的测试消息"
        )

    def handle(self, *args, **options):
        message = options["message"]
        self.stdout.write(f"发送：{message}")
        answer = llm_client.chat(message)
        self.stdout.write(self.style.SUCCESS(f"模型回答：{answer}"))
