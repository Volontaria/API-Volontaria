# Generated by Django 2.2.12 on 2020-08-01 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('volunteer', '0002_auto_20200727_2150'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='description',
            field=models.TextField(default=None, verbose_name='Description'),
            preserve_default=False,
        ),
    ]