from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from notifications.tasks import send_order_sms

@receiver(post_save, sender=Order)
def order_created_handler(sender, instance, created, **kwargs):
    # only trigger on creation or on specific status
    if created:
        send_order_sms.delay(instance.id)
    else:
        # optionally trigger on status change to 'completed' etc.
        pass