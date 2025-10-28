from rest_framework import serializers
from apps.notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model"""
    customer_name = serializers.CharField(source='customer.customer_name', read_only=True)
    cargo_tracking = serializers.CharField(source='cargo.tracking_number', read_only=True, allow_null=True)
    
    class Meta:
        model = Notification
        fields = ['notification_id', 'customer_id', 'customer_name', 'cargo_id',
                  'cargo_tracking', 'notification_type', 'delivery_method',
                  'content', 'status', 'sent_at', 'delivered_at']
        read_only_fields = ['notification_id', 'sent_at']

