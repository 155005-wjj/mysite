# Generated manually for create_time field type change (2026-10-23)
# DateTimeField -> DateField：与老师代码对齐，配合日历只选日期（yyyy-mm-dd）
# 数据影响：MySQL datetime(6) 列转为 date，时间部分（00:00:00）被截断，日期保留，无数据丢失。

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0002_prettynum'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='create_time',
            field=models.DateField(verbose_name='入职时间'),
        ),
    ]
