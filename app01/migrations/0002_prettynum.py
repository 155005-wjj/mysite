# Generated manually for PrettyNum model (2026-10-23)
# 注意：models.py 中 UserInfo.depart 与 0001_initial 存在既有差异（null/on_delete），
# 本次迁移不涉及该字段，保持数据库结构不变。

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = False

    dependencies = [
        ('app01', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PrettyNum',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mobile', models.CharField(max_length=11, verbose_name='手机号')),
                ('price', models.IntegerField(default=0, verbose_name='价格')),
                ('level', models.SmallIntegerField(choices=[(1, '1级'), (2, '2级'), (3, '3级'), (4, '4级')], default=1, verbose_name='级别')),
                ('status', models.SmallIntegerField(choices=[(1, '已占用'), (2, '未使用')], default=2, verbose_name='状态')),
            ],
        ),
    ]
