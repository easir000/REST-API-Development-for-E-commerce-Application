
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Order, OrderItem, Product
from .serializers import OrderSerializer, OrderItemSerializer, ProductSerializer

from .models import Review
from rest_framework import viewsets
from .models import Review
from .serializers import ReviewSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdminOrReadOnly
from rest_framework import permissions


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]  # Example: Only authenticated users can create reviews


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]



class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def add_product(self, request, pk=None):
        order = self.get_object()
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        # Add logic to update stock, handle order total, etc.

        order_item = OrderItem.objects.create(order=order, product=product, quantity=quantity, price=product.price)

        serializer = OrderItemSerializer(order_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # Additional actions for delete and update
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def place_order(self, request, pk=None):
        order = self.get_object()

        # Add logic to handle placing an order, update order status, etc.
        if order.status == Order.ORDER_STATUS_PENDING:
            order.status = Order.ORDER_STATUS_PLACED
            order.save()

            # Update stock quantity
            order_items = OrderItem.objects.filter(order=order)
            for order_item in order_items:
                product = order_item.product
                product.stock -= order_item.quantity
                product.save()

            return Response({'status': 'Order placed successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Order cannot be placed'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def update_order(self, request, pk=None):
        order = self.get_object()

        # Add logic to handle updating an order, update order status, etc.
        if order.status == Order.ORDER_STATUS_PLACED:
            order.status = Order.ORDER_STATUS_PROCESSING
            order.save()
            return Response({'status': 'Order updated successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Order cannot be updated'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def cancel_order(self, request, pk=None):
        order = self.get_object()

        # Add logic to handle canceling an order, update order status, etc.
        if order.status == Order.ORDER_STATUS_PLACED or order.status == Order.ORDER_STATUS_PROCESSING:
            order.status = Order.ORDER_STATUS_CANCELLED
            order.save()

            # Restore stock quantity
            order_items = OrderItem.objects.filter(order=order)
            for order_item in order_items:
                product = order_item.product
                product.stock += order_item.quantity
                product.save()

            return Response({'status': 'Order cancelled successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Order cannot be cancelled'}, status=status.HTTP_400_BAD_REQUEST)