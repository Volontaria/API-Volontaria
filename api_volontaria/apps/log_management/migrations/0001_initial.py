# Generated by Django 2.2.12 on 2020-07-24 01:49

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EmailLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_email', models.CharField(max_length=1024, verbose_name='User email')),
                ('type_email', models.CharField(max_length=1024, verbose_name='Type email')),
                ('nb_email_sent', models.IntegerField(verbose_name='Number email sent')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Creation date')),
            ],
            options={
                'verbose_name': 'Email Log',
                'verbose_name_plural': 'Email Logs',
            },
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.CharField(max_length=100, verbose_name='Source')),
                ('level', models.CharField(max_length=100, verbose_name='Level')),
                ('message', models.TextField(verbose_name='Message')),
                ('error_code', models.CharField(blank=True, max_length=100, null=True, verbose_name='Error Code')),
                ('additional_data', models.TextField(blank=True, null=True, verbose_name='Additional data')),
                ('traceback_data', models.TextField(blank=True, null=True, verbose_name='TraceBack')),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Creation date')),
            ],
            options={
                'verbose_name': 'Log',
                'verbose_name_plural': 'Logs',
            },
        ),
    ]
