from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order

@receiver(post_save, sender=Order)
def order_created_handler(sender, instance, created, **kwargs):
    if created:
        from notifications.tasks import send_order_sms  
        try:
            send_order_sms.delay(instance.id)
        except Exception as e:

            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to queue SMS task for Order {instance.id}: {e}")
