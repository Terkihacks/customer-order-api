from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
import africastalking
from orders.models import Order

logger = get_task_logger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_order_sms(self, order_id):
    """Minimal task: fetch order + send SMS."""
    try:
        order = Order.objects.select_related("customer").get(pk=order_id)
        phone = getattr(order.customer, "phone", None)
        if not phone:
            return logger.warning("No phone for order %s", order_id)

        message = (
            f"Hello {order.customer.name}, your order #{order.id} for {order.item} "
            f"has been received. Amount: {order.amount} at {order.order_time}."
        )

        africastalking.initialize(
            settings.AFRICASTALKING_USERNAME,
            settings.AFRICASTALKING_API_KEY
        )
        result = africastalking.SMS.send(
            message,
            [phone],
            sender_id=getattr(settings, "AFRICASTALKING_SENDER_ID", None)
        )

        logger.info("SMS sent for order %s: %s", order_id, result)
        return result

    except Order.DoesNotExist:
        logger.warning("Order %s not found", order_id)
    except Exception as exc:
        logger.error("SMS failed for order %s: %s", order_id, exc)
        raise self.retry(exc=exc, countdown=60)
