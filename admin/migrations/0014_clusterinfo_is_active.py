# Generated by Django 3.0.2 on 2020-03-29 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin', '0013_clusterinfo'),
    ]

    operations = [
        migrations.AddField(
            model_name='clusterinfo',
            name='is_active',
            field=models.BooleanField(default=False, verbose_name='是否激活'),
        ),
    ]