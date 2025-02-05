from rest_framework import serializers
from .models import SubscriptionPlan, Subscription

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id',
            'name',
            'description',
            'monthly_price',
            'max_seats',
            'is_active',
            'is_deleted',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'is_deleted', 'created_at', 'updated_at',
        ]


class SubscriptionSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    organization_name = serializers.CharField(
        source='organization.name', read_only=True
    )

    class Meta:
        model = Subscription
        fields = [
            'id',
            'organization',
            'organization_name',
            'plan',
            'plan_name',
            'start_date',
            'end_date',
            'is_deleted',
            'created_at',
            'updated_at',
            'is_active',
        ]
        read_only_fields = [
            'id', 'organization', 'organization_name',
            'is_deleted', 'created_at', 'updated_at', 'is_active',
        ]

    def update(self, instance, validated_data):
        """
        If you want to allow updating plan, seats, etc. This is an example approach.
        """
        return super().update(instance, validated_data)
