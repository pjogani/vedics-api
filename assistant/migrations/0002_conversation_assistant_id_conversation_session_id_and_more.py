# Generated by Django 5.1.5 on 2025-02-06 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assistant', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversation',
            name='assistant_id',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='conversation',
            name='session_id',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='conversation',
            name='thread_id',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
