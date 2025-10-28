from django.db import models
from apps.core.models import TimestampedModel


class Customer(TimestampedModel):
    customer_id = models.AutoField(primary_key=True)
    customer_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='customers')
    preferred_communication = models.CharField(max_length=20, choices=[
        ('whatsapp', 'WhatsApp'),
        ('sms', 'SMS'),
        ('email', 'Email'),
    ], default='whatsapp')
    
    class Meta:
        db_table = 'customers'
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
        
    def __str__(self):
        return self.customer_name

