from rest_framework import serializers
from .models import Order
from customers.models import Customer


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for reading orders (detailed response)."""
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    customer_code = serializers.CharField(source='customer.code', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'customer_name', 'customer_code',
            'item', 'amount', 'order_time', 'status', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'customer_name', 'customer_code']
        ordering = ['-created_at']  

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive")
        if value > 1_000_000:
            raise serializers.ValidationError("Order amount cannot exceed 1,000,000")
        return value


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating orders (minimal fields)."""

    class Meta:
        model = Order
        fields = ['customer', 'item', 'amount', 'order_time', 'status']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive")
        if value > 1_000_000:
            raise serializers.ValidationError("Order amount cannot exceed 1,000,000")
        return value
