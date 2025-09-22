from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
# Create your models here.

class OrderManager(models.Manager):
    def recent_orders(self):
        return self.order_by('-created_at')[:10]
    def customer_orders(self, customer_id):
        return self.filter(customer_id=customer_id).order_by('-created_at')
    def pending_orders(self):
        return self.filter(status='pending').select_related('customer').order_by('created_at')
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    item = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = OrderManager()

    class Meta:
        db_table = 'orders'
        ordering = ['-order_time']
        indexes = [
            models.Index(fields=['customer', '-order_time']),
            models.Index(fields=['status', '-created_at']),
        ]
    def clean(self):
        if self.item:
            self.item = self.item.strip()
        if self.order_time and self.order_time > timezone.now():
            raise ValidationError("Order time cannot be in the future")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        is_new = self.pk is None
        super().save(*args, **kwargs)

        # Trigger SMS for new orders only
        # if is_new and self.status == 'pending':
        #     from orders.tasks import send_order_sms
        #     send_order_sms.delay(self.id)
        