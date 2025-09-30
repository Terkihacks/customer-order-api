from django.test import TestCase

# Create your tests here.
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Customer
from .serializers import CustomerSerializer

User = get_user_model()

class CustomerSerializerTest(APITestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            name="Ray",
            code="RAY123",
            phone="254712345678"
        )

    def test_valid_serializer(self):
        data = {"name": "Test", "code": "ABC", "phone": "254711111111"}
        serializer = CustomerSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_code_lowercase(self):
        data = {"name": "Test", "code": "abc", "phone": "254711111111"}
        serializer = CustomerSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("Customer code must be uppercase.", str(serializer.errors))

    def test_invalid_phone_format(self):
        data = {"name": "Test", "code": "ABC", "phone": "0712345678"}
        serializer = CustomerSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("Phone number must start with +254", str(serializer.errors))

    def test_unique_code(self):
        data = {"name": "Another", "code": "RAY123", "phone": "254799999999"}
        serializer = CustomerSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("Customer code must be unique.", str(serializer.errors))


class CustomerAPITest(APITestCase):
    def setUp(self):
        # Create test user for authentication
        self.user = User.objects.create_user(username="tester", password="password123")
        self.client.login(username="tester", password="password123")

        # Create a sample customer
        self.customer = Customer.objects.create(
            name="Ray",
            code="RAY123",
            phone="254712345678"
        )

    def test_create_customer(self):
        url = reverse("customer-list")  
        data = {"name": "Test", "code": "ABC", "phone": "254799999999"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "Customer created successfully")

    def test_update_customer(self):
        url = reverse("customer-detail", args=[self.customer.id])
        data = {"name": "Updated Ray", "code": "RAY123", "phone": "254711111111"}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Customer updated successfully")

    def test_list_customers(self):
        url = reverse("customer-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_retrieve_customer(self):
        url = reverse("customer-detail", args=[self.customer.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.customer.id)

    def test_active_customers(self):
        url = reverse("customer-active")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_orders(self):
        url = reverse("customer-orders", args=[self.customer.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
