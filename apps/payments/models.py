from django.db import models
from apps.core.models import TimestampedModel


class Payment(TimestampedModel):
    payment_id = models.AutoField(primary_key=True)
    invoice = models.ForeignKey('invoices.Invoice', on_delete=models.CASCADE, related_name='payments')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_reference = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=50, choices=[
        ('mobile_money', 'Mobile Money'),
        ('bank', 'Bank Transfer'),
        ('cash', 'Cash'),
    ])
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], default='pending')
    processed_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='processed_payments')
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'payments'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Payment {self.payment_reference} - ${self.amount_paid}"


class Transaction(TimestampedModel):
    transaction_id = models.AutoField(primary_key=True)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=50, choices=[
        ('cargo_payment', 'Cargo Payment'),
        ('storage_fee', 'Storage Fee'),
        ('refund', 'Refund'),
        ('penalty', 'Penalty'),
    ])
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=[
        ('success', 'Success'),
        ('failed', 'Failed'),
    ])
    reference = models.CharField(max_length=100)
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='transactions')
    transaction_details = models.JSONField(blank=True, null=True, help_text="Additional transaction details like bank name, account number, etc.")
    
    class Meta:
        db_table = 'transactions'
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.transaction_type} - ${self.amount} - {self.status}"


class ReleaseOrder(TimestampedModel):
    release_order_id = models.AutoField(primary_key=True)
    cargo = models.ForeignKey('cargo.Cargo', on_delete=models.CASCADE, related_name='release_orders')
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='release_orders')
    release_code = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('used', 'Used'),
        ('expired', 'Expired'),
    ], default='active')
    generated_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='generated_release_orders')
    generated_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'release_orders'
        verbose_name = 'Release Order'
        verbose_name_plural = 'Release Orders'
        
    def __str__(self):
        return f"{self.release_code} - {self.cargo.tracking_number}"

