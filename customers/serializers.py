from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    # Enforce uniqueness of code with a clear error message
    code = serializers.CharField(
        max_length=50,
        validators=[
            UniqueValidator(
                queryset=Customer.objects.all(),
                message="Customer code must be unique."
            )
        ]
    )

    # Read-only computed field from model property
    total_orders = serializers.ReadOnlyField()

    class Meta:
        model = Customer
        fields = [
            "id", "name", "code", "phone", 
            "total_orders", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at", "total_orders"]

    # --- Field-level validation ---
    def validate_code(self, value: str) -> str:
        """
        Ensure customer code is uppercase and at least 3 characters long.
        """
        value = value.strip()
        if not value.isupper():
            raise serializers.ValidationError("Customer code must be uppercase.")
        if len(value) < 3:
            raise serializers.ValidationError("Customer code must be at least 3 characters.")
        return value

    def validate_phone(self, value: str) -> str: 
        """
        Ensure phone numbers follow Kenyan format (+254...).
        """
        if value and not value.startswith("+254"):
            raise serializers.ValidationError("Phone number must start with +254 for Kenyan numbers.")
        return value


