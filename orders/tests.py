from django.test import TestCase

# Create your tests here.

from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta
from unittest.mock import patch
from rest_framework import status, serializers
from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User

from orders.models import Order
from orders.serializers import OrderSerializer
from orders.views import OrderViewSet


# -------------------
# Model Tests
# -------------------
class OrderModelTest(TestCase):
    def test_item_is_stripped(self):
        order = Order(item="   Laptop   ", amount=500, order_time=timezone.now())
        order.clean()
        self.assertEqual(order.item, "Laptop")

    def test_order_time_cannot_be_in_future(self):
        future_time = timezone.now() + timedelta(days=1)
        order = Order(item="Phone", amount=200, order_time=future_time)
        with self.assertRaises(ValidationError):
            order.clean()


# -------------------
# Serializer Tests
# -------------------
class OrderSerializerTest(TestCase):
    def test_amount_must_be_positive(self):
        serializer = OrderSerializer(data={"item": "Book", "amount": -10})
        self.assertFalse(serializer.is_valid())
        self.assertIn("Amount must be positive", str(serializer.errors))

    def test_amount_cannot_exceed_limit(self):
        serializer = OrderSerializer(data={"item": "Car", "amount": 2_000_000})
        self.assertFalse(serializer.is_valid())
        self.assertIn("Order amount cannot exceed 1,000,000", str(serializer.errors))


# -------------------
# Business Logic (create_order)
# -------------------
class OrderCreateLogicTest(TestCase):
    @patch("Orders.views.logger.info")
    @patch("Orders.views.order_created_handler.send")
    def test_create_order_triggers_signal_and_logs(self, mock_signal, mock_logger):
        serializer = OrderSerializer(data={"item": "TV", "amount": 1000})
        serializer.is_valid(raise_exception=True)

        viewset = OrderViewSet()
        order = viewset.create_order(serializer)

        self.assertIsInstance(order, Order)
        mock_logger.assert_called_once()
        mock_signal.assert_called_once()


# -------------------
# View Action Tests (cancel)
# -------------------
class OrderCancelTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="ray", password="pass123")
        self.client.login(username="ray", password="pass123")
        self.order = Order.objects.create(item="Phone", amount=500, status="pending")

    def test_cancel_pending_order(self):
        url = reverse("order-cancel", args=[self.order.id])
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "cancelled")

    def test_cannot_cancel_non_pending_order(self):
        self.order.status = "completed"
        self.order.save()
        url = reverse("order-cancel", args=[self.order.id])
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Only pending orders can be cancelled", str(response.data))

