from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
import logging

from .models import Order
from .serializers import OrderSerializer, OrderCreateSerializer
# from events.serializers import EventSerializer

logger = logging.getLogger(__name__)


class OrderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing orders.
    Supports filtering, ordering, custom creation, and cancellation.
    """
    queryset = Order.objects.select_related("customer")
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["status", "customer__code"]
    ordering_fields = ["order_time", "amount", "created_at"]
    ordering = ["-order_time"]

    def get_serializer_class(self):
        """Use different serializers for create vs. read operations."""
        if self.action == "create":
            return OrderCreateSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        """
        Custom create logic:
        - Save order
        - Log creation
        - Trigger async SMS notification
        """
        order = serializer.save()
        logger.info(f"Order {order.id} created for customer {order.customer.code}")
        # Trigger an order_created event
         
         
    
        return order

    @action(detail=True, methods=["patch"])
    def cancel(self, request, pk=None):
        """
        Cancel an order (only if status is 'pending').
        """
        order = self.get_object()
        if order.status != "pending":
            return Response(
                {"error": "Only pending orders can be cancelled"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order.status = "cancelled"
        order.save(update_fields=["status"])
        logger.info(f"Order {order.id} was cancelled")

        serializer = self.get_serializer(order)
        return Response(serializer.data)
