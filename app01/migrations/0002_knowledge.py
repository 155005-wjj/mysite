# Generated for AI 智能助手课程设计：新增制度知识库 Knowledge 表

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Knowledge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=64, verbose_name='标题')),
                ('content', models.TextField(verbose_name='制度内容')),
            ],
            options={
                'verbose_name': '制度知识',
                'verbose_name_plural': '制度知识',
                'db_table': 'biz_knowledge',
            },
        ),
    ]
