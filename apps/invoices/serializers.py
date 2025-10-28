from rest_framework import serializers
from apps.invoices.models import Invoice, StorageFee


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for Invoice model"""
    cargo_tracking = serializers.CharField(source='cargo.tracking_number', read_only=True)
    customer_name = serializers.CharField(source='cargo.customer.customer_name', read_only=True)
    
    class Meta:
        model = Invoice
        fields = ['invoice_id', 'cargo_id', 'cargo_tracking', 'customer_name',
                  'control_number', 'amount', 'currency', 'due_date', 'status',
                  'payment_method', 'created_at', 'updated_at']
        read_only_fields = ['invoice_id', 'control_number', 'created_at', 'updated_at']


class StorageFeeSerializer(serializers.ModelSerializer):
    """Serializer for Storage Fee model"""
    
    class Meta:
        model = StorageFee
        fields = '__all__'

