# Generated by Django 3.0.2 on 2020-01-07 15:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('admin', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vminfo',
            old_name='cpu',
            new_name='vm_cpu',
        ),
        migrations.RenameField(
            model_name='vminfo',
            old_name='desc',
            new_name='vm_desc',
        ),
        migrations.RenameField(
            model_name='vminfo',
            old_name='memory',
            new_name='vm_memory',
        ),
        migrations.RenameField(
            model_name='vminfo',
            old_name='os',
            new_name='vm_os',
        ),
    ]
