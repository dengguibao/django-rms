# Generated by Django 3.0.2 on 2020-03-24 17:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin', '0008_hostinfo_cpu_core'),
    ]

    operations = [
        migrations.AddField(
            model_name='hostinfo',
            name='raid',
            field=models.CharField(max_length=50, null=True, verbose_name='raid'),
        ),
    ]
