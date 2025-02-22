# Generated by Django 5.1.5 on 2025-02-05 17:52

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Prediction",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("is_deleted", models.BooleanField(default=False)),
                ("created_by", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "created_by_role",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("updated_by", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "updated_by_role",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "created_by_organization",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "updated_by_organization",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                (
                    "updated_at",
                    models.DateTimeField(
                        blank=True, default=django.utils.timezone.now, null=True
                    ),
                ),
                ("access_list", models.JSONField(blank=True, default=list, null=True)),
                (
                    "allowed_internal_roles",
                    models.JSONField(blank=True, default=list, null=True),
                ),
                ("prediction_type", models.CharField(max_length=100)),
                ("content", models.JSONField()),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
