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
            name="ProfileQuestion",
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
                ("question_text", models.CharField(max_length=255)),
                ("question_type", models.CharField(blank=True, max_length=50)),
                ("help_text", models.TextField(blank=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="UserProfile",
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
                ("date_of_birth", models.DateField(blank=True, null=True)),
                ("time_of_birth", models.TimeField(blank=True, null=True)),
                ("place_of_birth", models.CharField(blank=True, max_length=255)),
                (
                    "latitude",
                    models.DecimalField(
                        blank=True, decimal_places=6, max_digits=9, null=True
                    ),
                ),
                (
                    "longitude",
                    models.DecimalField(
                        blank=True, decimal_places=6, max_digits=9, null=True
                    ),
                ),
                ("phone_number", models.CharField(blank=True, max_length=20)),
                ("birth_chart", models.JSONField(blank=True, default=dict)),
                ("preferred_language", models.CharField(default="en", max_length=10)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ProfileAnswer",
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
                ("answer_text", models.TextField(blank=True)),
                (
                    "question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="answers",
                        to="profiles.profilequestion",
                    ),
                ),
                (
                    "profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="answers",
                        to="profiles.userprofile",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
