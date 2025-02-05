import logging
import requests
from django.core.cache import cache
from django.shortcuts import get_object_or_404

from .models import Service, Endpoint, APIRequestLog

logger = logging.getLogger(__name__)

def handle_external_request(service_name, endpoint_name, method="GET", user=None,
                            param_values=None, request_data=None):
    """
    Generic function to handle an external request, logging it in APIRequestLog.
    This is a placeholder stripped of domain-specific logic.
    """
    if param_values is None:
        param_values = {}
    if request_data is None:
        request_data = {}

    service = get_object_or_404(Service, name=service_name)
    endpoint = get_object_or_404(Endpoint, service=service, name=endpoint_name, method=method)
    
    # Build URL
    url = service.base_url + endpoint.path
    # Possibly handle path_params or query_params here if needed
    query_params = param_values

    headers = {}
    if service.auth_method and service.auth_method.lower() == "bearer":
        # For example, read a token from environment or cache
        token = cache.get(f"{service_name}_token", "FAKE-TOKEN")
        headers["Authorization"] = f"Bearer {token}"

    # Execute request
    try:
        if method == "GET":
            res = requests.get(url, params=query_params, headers=headers)
        elif method == "POST":
            res = requests.post(url, json=request_data, headers=headers, params=query_params)
        elif method == "PUT":
            res = requests.put(url, json=request_data, headers=headers, params=query_params)
        elif method == "DELETE":
            res = requests.delete(url, headers=headers, params=query_params)
        else:
            raise ValueError("Unsupported method")

        status_code = res.status_code
        try:
            response_data = res.json()
        except Exception:
            response_data = {"raw": res.text}

        # Log the request
        APIRequestLog.objects.create(
            user=user if user and user.is_authenticated else None,
            service=service,
            endpoint=endpoint,
            full_url=res.url,
            request_data=request_data,
            response_data=response_data,
            status_code=status_code
        )

        return res

    except requests.exceptions.RequestException as e:
        logger.error(f"External request error: {str(e)}")
        raise e