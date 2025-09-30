from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

import logging
from .signals import order_created_handler

from .models import Order
from .serializers import OrderSerializer, OrderCreateSerializer
from rest_framework.permissions import IsAuthenticated

logger = logging.getLogger(__name__)


class OrderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing orders.
    Supports filtering, ordering, custom creation, and cancellation.
    """
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.select_related("customer")
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["status", "customer__code"]
    ordering_fields = ["order_time", "amount", "created_at"]
    ordering = ["-order_time"]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return OrderCreateSerializer
        return OrderSerializer


    def create_order(self, serializer):
        """
         Order create logic:
        - Save order
        - Log creation
        - Trigger async SMS notification
        """
        order = serializer.save()
        logger.info(f"Order {order.id} created for customer {order.customer.code}")
        # Trigger an order_created event and  Fire the signal
        order_created_handler.send(sender=self.__class__, order=order)
        return order

    @action(detail=True, methods=["patch"], permission_classes = [IsAuthenticated])
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
