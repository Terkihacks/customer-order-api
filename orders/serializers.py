from rest_framework import serializers
from .models import Order, Customer

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
    
    def validate_order_time(self, value):
        from django.utils import timezone
        if value > timezone.now():
            raise serializers.ValidationError("Order time cannot be in the future")
        return value
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive")
        if value > 1_000_000:  # clear formatting
            raise serializers.ValidationError("Order amount cannot exceed 1,000,000")
        return value

class OrderCreateSerializer(OrderSerializer):
    """Separate serializer for creation with different validation"""
    customer_code = serializers.CharField(write_only=True)
    
    def validate_customer_code(self, value):
        code = value.upper().strip()
        if not Customer.objects.filter(code=code).exists():
            raise serializers.ValidationError("Customer with this code does not exist")
        return code
    
    def create(self, validated_data):
        customer_code = validated_data.pop('customer_code')
        customer = Customer.objects.get(code=customer_code)
        validated_data['customer'] = customer
        return super().create(validated_data)
    
    def to_representation(self, instance):
        """Return full OrderSerializer response after creation"""
        return OrderSerializer(instance, context=self.context).data