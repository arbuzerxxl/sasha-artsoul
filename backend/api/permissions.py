from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsClient(BasePermission):

    def has_permission(self, request, view):
        return bool(request.method in SAFE_METHODS and request.user and request.user.is_authenticated or request.user.is_superuser)

    def has_object_permission(self, request, view, obj):
        if hasattr(obj.client, 'user'):
            if obj.client.user == request.user and request.method in SAFE_METHODS:
                return True
        return request.user.is_superuser
