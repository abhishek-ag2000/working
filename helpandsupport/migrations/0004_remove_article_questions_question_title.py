# Generated by Django 2.0.6 on 2019-06-12 08:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('helpandsupport', '0003_auto_20190611_1724'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article_questions',
            name='Question_title',
        ),
    ]
