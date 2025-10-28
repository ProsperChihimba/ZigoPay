from django.db import models
from apps.core.models import TimestampedModel
import uuid


def generate_tracking_number():
    from datetime import datetime
    return f"ZP-{datetime.now().year}-{uuid.uuid4().hex[:8].upper()}"


class Cargo(TimestampedModel):
    cargo_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE, related_name='cargo')
    warehouse = models.ForeignKey('warehouses.Warehouse', on_delete=models.CASCADE, related_name='cargo')
    tracking_number = models.CharField(max_length=50, unique=True, default=generate_tracking_number)
    cargo_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    origin_location = models.CharField(max_length=255)
    destination_location = models.CharField(max_length=255)
    cargo_weight = models.DecimalField(max_digits=10, decimal_places=2, help_text="Weight in kg")
    cargo_value = models.DecimalField(max_digits=10, decimal_places=2)
    container_id = models.CharField(max_length=100, blank=True, null=True)
    origin_tracking_number = models.CharField(max_length=100, blank=True, null=True)
    cbm = models.DecimalField(max_digits=10, decimal_places=2, help_text="Cubic meters")
    width = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    height = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('in_transit', 'In Transit'),
        ('arrived', 'Arrived'),
        ('delivered', 'Delivered'),
    ], default='pending')
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='created_cargo')
    
    class Meta:
        db_table = 'cargo'
        verbose_name = 'Cargo'
        verbose_name_plural = 'Cargo'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.tracking_number} - {self.cargo_name}"
    
    def save(self, *args, **kwargs):
        # Calculate CBM if dimensions are provided
        if self.length and self.width and self.height and not self.cbm:
            self.cbm = (float(self.length) * float(self.width) * float(self.height)) / 1000
        super().save(*args, **kwargs)


class CargoHistory(TimestampedModel):
    history_id = models.AutoField(primary_key=True)
    cargo = models.ForeignKey(Cargo, on_delete=models.CASCADE, related_name='history')
    previous_status = models.CharField(max_length=20, blank=True, null=True)
    new_status = models.CharField(max_length=20)
    updated_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='cargo_updates')
    remarks = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'cargo_history'
        verbose_name = 'Cargo History'
        verbose_name_plural = 'Cargo History'
        ordering = ['-updated_at']
        
    def __str__(self):
        return f"{self.cargo.tracking_number} - {self.previous_status} -> {self.new_status}"

