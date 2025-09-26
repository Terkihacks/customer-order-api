from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from .models import Customer
from .serializers import CustomerSerializer
from rest_framework.permissions import IsAuthenticated

class CustomerViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing customers.
    Provides:
    - Standard CRUD operations
    - Filtering, searching, ordering
    - Custom actions for orders and active customers
    """
    permission_classes = [IsAuthenticated]
    queryset = Customer.objects.all() 
    serializer_class = CustomerSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['code', 'phone']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Optimize queryset based on action:
        - List: only load lightweight fields
        - Retrieve/detail: include related orders
        """
        queryset = Customer.objects.all()

        if self.action == 'list':
            return queryset.only('id', 'name', 'code', 'phone', 'created_at')

        return queryset.prefetch_related('orders')

    def create(self, request, *args, **kwargs):
        """
        Customer create with clear validation handling. 
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(
            {"message": "Customer created successfully", "data": serializer.data},
            status=status.HTTP_201_CREATED,
            headers=headers
        )
   
    def update(self, request, *args, **kwargs):
        """
        Customer update with success message.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)

        return Response(
            {"message": "Customer updated successfully", "data": serializer.data},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['get'], url_path="orders",permission_classes=[IsAuthenticated])
    def orders(self, request, pk=None):
        """Get all orders for a specific customer"""
        customer = self.get_object()
        orders = customer.orders.all()
        
        # Pagination for orders
        page = self.paginate_queryset(orders)
        from orders.serializers import OrderSerializer
        if page is not None:
            serializer = OrderSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    @action(detail=False, methods=['get'], url_path="active", permission_classes=[IsAuthenticated])
    def active(self, request):
        """
        Get customers who have placed recent orders.
        Uses a custom manager method `Customer.objects.active_customers()`.
        """
        active_customers = Customer.objects.active_customers()
        serializer = self.get_serializer(active_customers, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

