from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
import africastalking
from .models import SMSNotification
from orders.models import Order

logger = get_task_logger(__name__)

@shared_task(bind=True, max_retries=5, default_retry_delay=60)
def send_order_sms(self, order_id):
    try:
        order = Order.objects.select_related("customer").get(pk=order_id)
    except Order.DoesNotExist:
        logger.warning("Order %s not found, abort SMS", order_id)
        return

    to = getattr(order.customer, "phone", None)
    if not to:
        logger.warning("Order %s customer has no phone", order_id)
        return

    message = f"Hello {order.customer.name}, your order #{order.id} for {order.item} has been received. Amount: {order.amount} at {order.order_time}."

    # create or get notification record
    notif, _ = SMSNotification.objects.get_or_create(order_id=order.id, to=to, defaults={"message": message})

    # init africastalking client
    africastalking.initialize(settings.AFRICASTALKING_USERNAME, settings.AFRICASTALKING_API_KEY)
    sms = africastalking.SMS

    try:
        notif.attempts += 1
        notif.save(update_fields=["attempts", "updated_at"])

        result = sms.send(message, [to], sender_id=getattr(settings, "AFRICASTALKING_SENDER_ID", None))
        notif.status = "sent"
        notif.last_error = ""
        notif.save(update_fields=["status", "last_error", "updated_at"])
        logger.info("SMS sent for order %s: %s", order_id, result)
        return result
    except Exception as exc:
        notif.status = "failed"
        notif.last_error = str(exc)[:2000]
        notif.save(update_fields=["status", "last_error", "updated_at"])
        logger.exception("SMS send failed for order %s (attempt %s)", order_id, notif.attempts)
        
        countdown = min(2 ** self.request.retries * 60, 3600)
        raise self.retry(exc=exc, countdown=countdown)

