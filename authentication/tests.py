from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from customers.models import Customer
from rest_framework_simplejwt.tokens import RefreshToken


class AuthFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.customer = Customer.objects.create_user(
            email="test@example.com", name="Tester", password="pass123", code="auth0|123"
        )
        self.refresh = RefreshToken.for_user(self.customer)

    def test_refresh_token(self):
        response = self.client.post(reverse("token_refresh"), {"refresh": str(self.refresh)})
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.json())

    def test_invalid_refresh_token(self):
        response = self.client.post(reverse("token_refresh"), {"refresh": "fake-token"})
        self.assertEqual(response.status_code, 400)

    def test_login_redirect(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 302)  # redirect to Auth0

    def test_logout_redirect(self):
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)
