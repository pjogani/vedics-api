import re
from threading import local

from django.conf import settings
from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
from django.utils.translation import activate

# If you have an Organization model, import it
# from profiles.models import Organization

_thread_locals = local()

def set_thread_value(key, value):
    setattr(_thread_locals, key, value)

def get_thread_value(key):
    return getattr(_thread_locals, key, None)

def clear_thread_locals():
    for attr in ("request","organization","current_role"):
        if hasattr(_thread_locals, attr):
            delattr(_thread_locals, attr)

def get_current_request():
    """returns the request object for this thread"""
    return getattr(_thread_locals, "request", None)

def get_current_user():
    """returns the current user, if exist, otherwise returns None"""
    request = get_current_request()
    if request:
        return getattr(request, "user", None)

def get_current_organization():
    return get_thread_value("organization")

def get_current_role():
    return get_thread_value("current_role")

class UpstreamUserContextMiddleware(MiddlewareMixin):
    """
    Example: parse custom X-User-ID, X-User-Roles, X-External-IDs, etc. from headers
    and store them in the request (and/or thread local) if needed.
    """
    def process_request(self, request):
        _thread_locals.request = request

        # Optionally parse some custom headers
        user_id = request.META.get("HTTP_X_USER_ID", "")
        if user_id:
            # Potentially do something with it, or rely on a custom auth
            pass

    def process_response(self, request, response):
        clear_thread_locals()
        return response

class LanguageMiddleware(MiddlewareMixin):
    """
    Sets language based on Accept-Language or a custom header.
    """
    def process_request(self, request):
        user_language = request.META.get("HTTP_ACCEPT_LANGUAGE") or request.headers.get("Accept-Language")
        if user_language:
            activate(user_language)

class OrganizationAndRoleMiddleware(MiddlewareMixin):
    """
    Attempt to identify the organization & user role from the request or hostname,
    storing them in thread-local for easy retrieval in signals or audits.
    """
    def process_request(self, request):
        _thread_locals.request = request

        # Example approach: read a custom header
        org_id = request.META.get("HTTP_X_ORGANIZATION_ID", "")
        role_header = request.META.get("HTTP_X_ROLE", "").strip()

        # If no org_id, fallback to hostname
        if not org_id:
            # host_and_port = request.get_host()
            # hostname = re.sub(r":\d+$", "", host_and_port)
            # Possibly lookup Organization by hostname
            # organization = Organization.objects.filter(hostname=hostname).first()
            organization = None
        else:
            # Try fetch from DB if needed
            # organization = Organization.objects.filter(pk=org_id).first()
            organization = None

        set_thread_value("organization", organization)
        set_thread_value("current_role", role_header)

    def process_response(self, request, response):
        clear_thread_locals()
        return response
