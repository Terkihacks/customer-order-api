from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from unittest.mock import patch, MagicMock
from django.conf import settings
from orders.models import Order
from customers.models import Customer
from notifications.tasks import send_order_sms


class SendOrderSmsTaskTest(TestCase):
    def setUp(self):
        # Create a customer + order for tests
        self.customer = Customer.objects.create(name="Ray", phone="254700000000")
        self.order = Order.objects.create(
            customer=self.customer,
            item="Laptop",
            amount=50000,
            order_time="2025-09-30 12:00:00"
        )

    @patch("notifications.tasks.africastalking")
    def test_sms_sent_when_order_exists(self, mock_africastalking):
        mock_sms = MagicMock()
        mock_africastalking.SMS = mock_sms

        result = send_order_sms(self.order.id)

        mock_africastalking.initialize.assert_called_once_with(
            settings.AFRICASTALKING_USERNAME,
            settings.AFRICASTALKING_API_KEY,
        )
        mock_sms.send.assert_called_once()
        self.assertIsNotNone(result)

    @patch("notifications.tasks.logger")
    def test_no_phone_logs_warning(self, mock_logger):
        self.customer.phone = None
        self.customer.save()

        result = send_order_sms(self.order.id)

        mock_logger.warning.assert_called_with("No phone for order %s", self.order.id)
        self.assertIsNone(result)

    @patch("notifications.tasks.logger")
    def test_order_not_found_logs_warning(self, mock_logger):
        send_order_sms(9999)  # invalid order_id
        mock_logger.warning.assert_called_with("Order %s not found", 9999)

    @patch("notifications.tasks.africastalking.SMS.send", side_effect=Exception("API Down"))
    @patch("notifications.tasks.logger")
    def test_sms_failure_retries(self, mock_logger, mock_sms_send):
        # Bind=True means first arg is 'self' (the task instance), so we pass a dummy with .retry
        class DummyTask:
            def retry(self, exc, countdown):
                raise Exception("Retry called")

        with self.assertRaises(Exception) as ctx:
            send_order_sms(DummyTask(), self.order.id)

        self.assertIn("Retry called", str(ctx.exception))
        mock_logger.error.assert_called()
