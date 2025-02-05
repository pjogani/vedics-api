# Generated by Django 5.1.5 on 2025-02-01 11:50

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Organization",
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
                ("name", models.CharField(max_length=255, unique=True)),
                (
                    "subscription_plan",
                    models.CharField(blank=True, default="free", max_length=100),
                ),
                ("seats", models.PositiveIntegerField(default=5)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Team",
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
                ("name", models.CharField(max_length=255)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="TeamMembership",
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
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("admin", "Admin"),
                            ("member", "Member"),
                            ("owner", "Owner"),
                        ],
                        default="member",
                        max_length=20,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
