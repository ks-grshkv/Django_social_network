# Generated by Django 2.2.19 on 2022-04-25 22:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_auto_20220425_1454'),
    ]

    operations = [
        migrations.RenameField(
            model_name='group',
            old_name='decription',
            new_name='description',
        ),
        migrations.RenameField(
            model_name='group',
            old_name='slug_address',
            new_name='slug',
        ),
    ]
