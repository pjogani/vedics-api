from collections import OrderedDict
import mimetypes
from urllib import parse

from django.conf import settings
from django.db import models
from django.http import HttpResponse
from django.template.loader import get_template
from django.utils import timezone
from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.utils.urls import remove_query_param, replace_query_param

# Merge best from Aegis and Aether
CONTENT_TYPE_JSON = "application/json; charset=utf-8"

class BaseApiMixin:
    """
    Provides standardized response utilities:
      - success, error, forbidden, not found, etc.
      - can be inherited by DRF view classes
    """
    def error_response(self, message="", errors=None, status_code=status.HTTP_400_BAD_REQUEST):
        return Response(
            {"response": message, "errors": errors},
            status=status_code,
            content_type=CONTENT_TYPE_JSON,
        )

    def forbidden_response(
        self,
        message="Access denied",
        errors=None,
        status_code=status.HTTP_403_FORBIDDEN,
    ):
        return Response(
            {"message": message, "errors": errors},
            status=status_code,
            content_type=CONTENT_TYPE_JSON,
        )

    def successful_post_response(self, message="", status_code=status.HTTP_201_CREATED):
        return Response(message, status=status_code, content_type=CONTENT_TYPE_JSON)

    def successful_no_content_response(self, message="", status_code=status.HTTP_204_NO_CONTENT):
        return Response({"message": message}, status=status_code, content_type=CONTENT_TYPE_JSON)

    def successful_response(self, message="", status_code=status.HTTP_200_OK):
        return Response({"message": message}, status=status_code, content_type=CONTENT_TYPE_JSON)

    def not_found_response(self, message="Not found", status_code=status.HTTP_404_NOT_FOUND):
        return Response({"message": message}, status=status_code, content_type=CONTENT_TYPE_JSON)

    def successful_get_response(self, message="", status_code=status.HTTP_200_OK):
        return Response(message, status=status_code, content_type=CONTENT_TYPE_JSON)

    def err_response(
        self,
        message="Request failed",
        errors=None,
        status_code=status.HTTP_400_BAD_REQUEST,
    ):
        return Response(
            {"message": message, "errors": errors},
            status=status_code,
            content_type=CONTENT_TYPE_JSON,
        )

    def redirect_response(self, url="", errors=None, status_code=status.HTTP_301_MOVED_PERMANENTLY):
        response = Response(status=status_code)
        response["Location"] = url
        return response

    def unauthorised_response(self, message=None, status_code=status.HTTP_401_UNAUTHORIZED):
        return Response(message, status=status_code, content_type=CONTENT_TYPE_JSON)

    def access_denied_response(self, error="Access Denied.", status_code=status.HTTP_403_FORBIDDEN):
        return Response(
            {"status_code": status_code, "error": error},
            status=status_code,
            content_type=CONTENT_TYPE_JSON,
        )

    def internal_error_response(self, error, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR):
        return Response(
            {"status_code": status.HTTP_500_INTERNAL_SERVER_ERROR, "error": error},
            status=status_code,
            content_type=CONTENT_TYPE_JSON,
        )

    def get_html(self, template, data):
        return get_template(template).render(data)

    def html_response(self, template, data):
        html = self.get_html(template, data)
        return HttpResponse(html)

    def paginated_ledger_response(self, request, data):
        """
        Override next & previous URL before sending the response (example method).
        """
        for key in ("next", "previous"):
            url = data.get(key)
            if url:
                params = parse.parse_qs(parse.urlparse(url).query)
                limit = params.get("limit", ["10"])[0]
                url = request.build_absolute_uri()
                url = replace_query_param(url, "limit", limit)

                if "offset" in params:
                    offset = params["offset"][0]
                    url = replace_query_param(url, "offset", offset)
                else:
                    url = remove_query_param(url, "offset")
                data[key] = url

        return self.successful_get_response(data)

    def render_file_redirect_response(
        self, url="", content_type=None, errors=None, status_code=status.HTTP_301_MOVED_PERMANENTLY
    ):
        """
        Renders a file redirect response with appropriate Content-Disposition header.
        """
        if hasattr(self, 'request') and self.request.query_params.get("download") == "true":
            content_disposition = "attachment"
        else:
            content_disposition = "inline"

        response = Response(status=status_code)
        if not content_type:
            content_type, _ = mimetypes.guess_type(url)
        if content_type:
            response["Content-Type"] = content_type

        response["Location"] = url
        response["Content-Disposition"] = f'{content_disposition}; filename="{url.split("/")[-1]}"'
        return response


class LimitSetPagination(LimitOffsetPagination):
    """
    A more flexible pagination class that also returns total_pages and current_page.
    """
    page_size = 25
    default_limit = 25

    def get_paginated_response(self, data):
        if self.count % self.limit:
            total_pages = int(self.count / self.limit) + 1
        else:
            total_pages = int(self.count / self.limit)
        current_page = int(self.offset / self.limit) + 1

        return Response(
            OrderedDict(
                [
                    ("count", self.count),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("total_pages", total_pages),
                    ("current_page", current_page),
                    ("results", data),
                ]
            )
        )


##
# Auditing / Deletion Mixins
#
class IsDeletedManager(models.Manager):
    """
    Custom manager to auto-filter out records marked as deleted.
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class IsDeletedMixin(models.Model):
    """
    Mixin to mark records as logically deleted
    instead of physically removing them from DB.
    """
    is_deleted = models.BooleanField(default=False)

    objects = IsDeletedManager()

    class Meta:
        abstract = True

class AuthorTimeStampedModel(IsDeletedMixin):
    """
    Enhanced auditing fields:
      - created_by, updated_by
      - created_at, updated_at
      - optional: role, organization
      - option to store 'access_list' or 'allowed_internal_roles'
    """

    created_by = models.CharField(max_length=255, null=True, blank=True)
    created_by_role = models.CharField(max_length=255, null=True, blank=True)
    updated_by = models.CharField(max_length=255, null=True, blank=True)
    updated_by_role = models.CharField(max_length=255, null=True, blank=True)
    created_by_organization = models.CharField(max_length=255, null=True, blank=True)
    updated_by_organization = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(default=timezone.now, null=True, blank=True)
    access_list = models.JSONField(default=list, blank=True, null=True)
    allowed_internal_roles = models.JSONField(default=list, blank=True, null=True)

    class Meta:
        abstract = True

    def soft_delete(self):
        if isinstance(self, IsDeletedMixin):
            self.is_deleted = True
            self.save(update_fields=['is_deleted'])
        else:
            raise TypeError("soft_delete is only valid if you also inherit from IsDeletedMixin.")