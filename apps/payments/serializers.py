from rest_framework import serializers
from apps.payments.models import Payment, Transaction, ReleaseOrder, Wallet, WalletTransaction


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


class WalletSerializer(serializers.ModelSerializer):
    """Serializer for Wallet model"""
    customer_name = serializers.CharField(source='customer.customer_name', read_only=True)
    customer_id = serializers.IntegerField(source='customer.customer_id', read_only=True)
    
    class Meta:
        model = Wallet
        fields = ['wallet_id', 'customer_id', 'customer_name', 'balance', 'currency',
                  'is_active', 'auto_payment_enabled', 'created_at', 'updated_at']
        read_only_fields = ['wallet_id', 'balance', 'created_at', 'updated_at']


class WalletTransactionSerializer(serializers.ModelSerializer):
    """Serializer for Wallet Transaction model"""
    customer_name = serializers.CharField(source='wallet.customer.customer_name', read_only=True)
    invoice_control = serializers.CharField(source='invoice.control_number', read_only=True, allow_null=True)
    
    class Meta:
        model = WalletTransaction
        fields = ['transaction_id', 'wallet_id', 'customer_name', 'transaction_type',
                  'amount', 'balance_before', 'balance_after', 'reference', 'description',
                  'invoice_id', 'invoice_control', 'payment_id', 'status', 'gateway_response',
                  'created_at']
        read_only_fields = ['transaction_id', 'created_at']

