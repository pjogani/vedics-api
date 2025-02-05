import logging
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .utils import handle_external_request
from .models import Service, Endpoint, APIRequestLog
from .serializers import ServiceSerializer, EndpointSerializer, APIRequestLogSerializer

logger = logging.getLogger(__name__)

class ServiceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

class EndpointViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Endpoint.objects.all()
    serializer_class = EndpointSerializer

class APIRequestLogViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = APIRequestLog.objects.all()
    serializer_class = APIRequestLogSerializer

class ExternalCallViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def call(self, request):
        """
        Example endpoint to demonstrate calling an external service
        by specifying service_name and endpoint_name in the request body.
        """
        service_name = request.data.get('service_name')
        endpoint_name = request.data.get('endpoint_name')
        method = request.data.get('method', 'GET').upper()
        param_values = request.data.get('param_values', {})
        body = request.data.get('body', {})

        res = handle_external_request(service_name, endpoint_name, method,
                                      user=request.user,
                                      param_values=param_values,
                                      request_data=body)
        try:
            data = res.json()
        except:
            data = {"raw": res.text}
        return Response(data, status=res.status_code)