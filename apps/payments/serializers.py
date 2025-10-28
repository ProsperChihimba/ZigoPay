from rest_framework import serializers
from apps.payments.models import Payment, Transaction, ReleaseOrder


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment model"""
    invoice_control = serializers.CharField(source='invoice.control_number', read_only=True)
    cargo_tracking = serializers.CharField(source='invoice.cargo.tracking_number', read_only=True)
    customer_name = serializers.CharField(source='invoice.cargo.customer.customer_name', read_only=True)
    
    class Meta:
        model = Payment
        fields = ['payment_id', 'invoice_id', 'invoice_control', 'cargo_tracking',
                  'customer_name', 'amount_paid', 'payment_reference', 'payment_method',
                  'status', 'processed_at', 'created_at']
        read_only_fields = ['payment_id', 'processed_at', 'created_at']


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for Transaction model"""
    
    class Meta:
        model = Transaction
        fields = '__all__'


class ReleaseOrderSerializer(serializers.ModelSerializer):
    """Serializer for Release Order model"""
    cargo_tracking = serializers.CharField(source='cargo.tracking_number', read_only=True)
    customer_name = serializers.CharField(source='cargo.customer.customer_name', read_only=True)
    
    class Meta:
        model = ReleaseOrder
        fields = ['release_order_id', 'release_code', 'cargo_id', 'cargo_tracking',
                  'customer_name', 'payment_id', 'status', 'generated_at', 'used_at']
        read_only_fields = ['release_order_id', 'release_code', 'generated_at']

