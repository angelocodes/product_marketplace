from rest_framework import permissions


class IsAdminOrOwner(permissions.BasePermission):
    """
    Custom permission to only allow admins or owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Superusers can do anything
        if request.user.is_superuser:
            return True
        # Admins can do anything
        if request.user.role == 'admin':
            return True
        # Owners can edit their own objects
        return obj.created_by == request.user


class IsApprover(permissions.BasePermission):
    """
    Only approvers can approve products.
    """

    def has_permission(self, request, view):
        # Superusers can do anything
        if request.user.is_superuser:
            return True
        return request.user.role == 'approver'


class CanCreateProduct(permissions.BasePermission):
    """
    Users with editor or higher role can create products.
    """

    def has_permission(self, request, view):
        # Superusers can do anything
        if request.user.is_superuser:
            return True
        return request.user.role in ['admin', 'editor', 'approver']


class CanViewAllProducts(permissions.BasePermission):
    """
    Admins and approvers can view all products, others only their business's.
    """

    def has_permission(self, request, view):
        # Superusers can do anything
        if request.user.is_superuser:
            return True
        return request.user.role in ['admin', 'approver']
