from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import User, Business, Product
from .serializers import UserSerializer, BusinessSerializer, ProductSerializer
from .permissions import IsAdminOrOwner, IsApprover, CanCreateProduct, CanViewAllProducts


class BusinessViewSet(viewsets.ModelViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Users can only see their own business, except admins
        if self.request.user.role == 'admin':
            return Business.objects.all()
        return Business.objects.filter(id=self.request.user.business.id) if self.request.user.business else Business.objects.none()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Business admins can see users in their business
        if self.request.user.role == 'admin':
            return User.objects.filter(business=self.request.user.business)
        return User.objects.none()

    def perform_create(self, serializer):
        # Set business to the current user's business
        serializer.save(business=self.request.user.business)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, CanCreateProduct]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'created_at', 'status']

    def get_queryset(self):
        # Internal view: show products based on permissions
        if self.request.user.role in ['admin', 'approver']:
            return Product.objects.all()
        elif self.request.user.role in ['editor']:
            return Product.objects.filter(business=self.request.user.business)
        else:
            return Product.objects.filter(business=self.request.user.business, status='approved')

    def perform_create(self, serializer):
        if not self.request.user.business:
            return Response(
                {"error": "You must be assigned to a business before creating products. Please contact an administrator."},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save(business=self.request.user.business)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            # For listing and retrieving, allow based on role
            return [IsAuthenticated()]
        elif self.action == 'approve':
            return [IsAuthenticated(), IsApprover()]
        else:
            return [IsAuthenticated(), CanCreateProduct(), IsAdminOrOwner()]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.role not in ['admin'] and instance.created_by != request.user:
            return Response({"detail": "You do not have permission to edit this product."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.role not in ['admin'] and instance.created_by != request.user:
            return Response({"detail": "You do not have permission to delete this product."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsApprover])
    def approve(self, request, pk=None):
        product = self.get_object()
        if product.status != 'pending_approval':
            return Response({"detail": "Product is not pending approval."}, status=status.HTTP_400_BAD_REQUEST)
        product.status = 'approved'
        product.save()
        serializer = self.get_serializer(product)
        return Response(serializer.data)


class PublicProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(status='approved')
    serializer_class = ProductSerializer
    permission_classes = []  # No authentication required for public view
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'created_at']
