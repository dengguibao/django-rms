# Generated by Django 3.0.2 on 2020-03-30 09:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin', '0020_auto_20200330_0916'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hostinfo',
            name='memory_size',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='hostinfo',
            name='memory_total_size',
            field=models.IntegerField(default=1),
        ),
    ]