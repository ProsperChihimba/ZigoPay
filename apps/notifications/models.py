from django.db import models
from apps.core.models import TimestampedModel


class Notification(TimestampedModel):
    notification_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE, related_name='notifications')
    cargo = models.ForeignKey('cargo.Cargo', on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    notification_type = models.CharField(max_length=50, choices=[
        ('registration', 'Cargo Registration'),
        ('loading', 'Cargo Loading'),
        ('transit', 'In Transit'),
        ('arrival', 'Cargo Arrival'),
        ('invoice', 'Invoice Sent'),
        ('payment_reminder', 'Payment Reminder'),
        ('payment_confirmed', 'Payment Confirmed'),
        ('release_order', 'Release Order Generated'),
        ('collection_reminder', 'Collection Reminder'),
    ])
    delivery_method = models.CharField(max_length=20, choices=[
        ('whatsapp', 'WhatsApp'),
        ('sms', 'SMS'),
        ('email', 'Email'),
    ])
    content = models.TextField()
    status = models.CharField(max_length=20, choices=[
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
    ], default='sent')
    sent_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')
    sent_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-sent_at']
        
    def __str__(self):
        return f"{self.notification_type} to {self.customer.customer_name} via {self.delivery_method}"

