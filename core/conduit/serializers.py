from rest_framework import serializers
from .models import Service, Endpoint, APIRequestLog

class EndpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Endpoint
        fields = "__all__"

class ServiceSerializer(serializers.ModelSerializer):
    endpoints = EndpointSerializer(many=True, read_only=True)

    class Meta:
        model = Service
        fields = ["id", "name", "base_url", "auth_method", "endpoints"]

class APIRequestLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIRequestLog
        fields = "__all__"