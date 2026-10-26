# Generated manually for Admin model (2026-10-26)
# 注意：models.py 中 UserInfo.depart 与 0001_initial 存在既有差异（null/on_delete），
# 本次迁移不涉及该字段，保持数据库结构不变。

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0003_alter_userinfo_create_time'),
    ]

    operations = [
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=32, verbose_name='用户名')),
                ('password', models.CharField(max_length=64, verbose_name='密码')),
            ],
        ),
    ]
