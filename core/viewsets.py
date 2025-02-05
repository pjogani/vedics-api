from rest_framework import viewsets
from .mixins import BaseApiMixin


class BaseModelViewSet(BaseApiMixin, viewsets.ModelViewSet):
    """
    A base ViewSet that integrates BaseApiMixin for consistent JSON responses.
    Inherit this in new apps or existing ones to maintain a standardized API format.
    """
    pass
