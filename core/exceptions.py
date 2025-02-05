from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Custom exception handler to ensure a consistent error response format.
    """
    response = exception_handler(exc, context)

    if response is not None:
        data = {
            "message": "Error",
            "errors": response.data,
            "status_code": response.status_code,
        }
        response.data = data

    return response


class CustomApiException(APIException):
    """
    Example custom exception that can be raised within views.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "A server error occurred."
    default_code = "error"
