import logging
import importlib

from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from core.mixins import AuthorTimeStampedModel  # <-- Imported the auditing mixin

logger = logging.getLogger(__name__)

class Service(AuthorTimeStampedModel):
    """
    Represents an external service.
    """
    name = models.CharField(max_length=100, unique=True)
    base_url = models.URLField(max_length=255, blank=True)
    auth_method = models.CharField(max_length=100, default="Bearer")

    def __str__(self):
        return self.name

class Handler(AuthorTimeStampedModel):
    """
    Represents a method or function that can process
    responses/requests for a given endpoint.
    """
    app_name = models.CharField(max_length=100)
    model_name = models.CharField(max_length=255)
    method_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.app_name}.{self.model_name}.{self.method_name}"

class Endpoint(AuthorTimeStampedModel):
    """
    Represents a route to be used when calling an external service.
    """
    METHODS = (("GET", "GET"), ("POST", "POST"), ("PUT", "PUT"), ("DELETE", "DELETE"))
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="endpoints"
    )
    name = models.CharField(max_length=255)
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=10, choices=METHODS)
    path_params = models.JSONField(default=list, blank=True, null=True)
    description = models.TextField(blank=True)
    handlers = models.ManyToManyField(
        Handler,
        related_name="endpoints",
        blank=True
    )
    extra_params = models.JSONField(default=dict, blank=True, null=True)

    def __str__(self):
        return f"{self.service.name} - {self.name} ({self.method})"

class APIRequestLog(AuthorTimeStampedModel):
    """
    Logs calls made to external services for auditing/troubleshooting.
    """
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    endpoint = models.ForeignKey(
        Endpoint,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    full_url = models.TextField(default="")
    request_data = models.JSONField(default=dict)
    response_data = models.JSONField(default=dict)
    status_code = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        user_display = self.user.username if self.user else "Anonymous"
        return f"API log by {user_display} on {self.timestamp}"
