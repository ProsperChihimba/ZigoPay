from django.db import models
from apps.core.models import TimestampedModel


class Warehouse(TimestampedModel):
    warehouse_id = models.AutoField(primary_key=True)
    warehouse_name = models.CharField(max_length=255)
    location = models.CharField(max_length=500)
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='warehouses')
    manager = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_warehouses')
    capacity = models.DecimalField(max_digits=10, decimal_places=2, help_text="Capacity in tons")
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('full', 'Full')
    ], default='active')
    
    class Meta:
        db_table = 'warehouses'
        verbose_name = 'Warehouse'
        verbose_name_plural = 'Warehouses'
        
    def __str__(self):
        return f"{self.warehouse_name} ({self.organization.name})"

