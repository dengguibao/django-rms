# Generated by Django 3.0.2 on 2020-03-29 17:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin', '0015_auto_20200329_1027'),
    ]

    operations = [
        migrations.AddField(
            model_name='vminfo',
            name='vm_status',
            field=models.IntegerField(default=0, verbose_name='虚拟机状态'),
        ),
    ]
