from rest_framework import serializers
from .models import Order
from customers.models import Customer

class OrderSerializer(serializers.ModelSerializer):
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
        if value > 1_000_000:  # clear formatting
            raise serializers.ValidationError("Order amount cannot exceed 1,000,000")
        return value