from django.db import models
from apps.core.models import TimestampedModel
import uuid
from datetime import datetime, timedelta


def generate_control_number():
    """Generate unique control number for invoices"""
    timestamp = datetime.now().strftime('%y%m%d')
    unique_id = uuid.uuid4().hex[:6].upper()
    return f"ZP-{timestamp}-{unique_id}"


class Invoice(TimestampedModel):
    invoice_id = models.AutoField(primary_key=True)
    cargo = models.ForeignKey('cargo.Cargo', on_delete=models.CASCADE, related_name='invoices')
    control_number = models.CharField(max_length=100, unique=True, default=generate_control_number)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ], default='pending')
    payment_method = models.CharField(max_length=50, blank=True, null=True, choices=[
        ('mobile_money', 'Mobile Money'),
        ('bank', 'Bank Transfer'),
        ('cash', 'Cash'),
    ])
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='created_invoices')
    
    class Meta:
        db_table = 'invoices'
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.control_number} - ${self.amount}"
    
    def is_overdue(self):
        """Check if invoice is overdue"""
        return self.status == 'pending' and self.due_date < datetime.now().date()


class StorageFee(TimestampedModel):
    storage_fee_id = models.AutoField(primary_key=True)
    cargo = models.ForeignKey('cargo.Cargo', on_delete=models.CASCADE, related_name='storage_fees')
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2)
    days_stored = models.IntegerField()
    total_fee = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('paid', 'Paid'),
    ], default='pending')
    calculated_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='calculated_fees')
    calculated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'storage_fees'
        verbose_name = 'Storage Fee'
        verbose_name_plural = 'Storage Fees'
        
    def __str__(self):
        return f"Storage Fee for {self.cargo.tracking_number} - ${self.total_fee}"

