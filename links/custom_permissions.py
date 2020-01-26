from rest_framework import permissions
from .models import Link
from django.contrib.auth.models import User
from .serializers import UserSerializer, LinkSerializer

class IsOwner(permissions.BasePermission):

    def has_permission(self, request, view):
        user = UserSerializer(request.user).data
        is_owner = Link.objects.filter(slug=view.kwargs['slug']).filter(user_id = user['id']).exists()
        return is_owner

class IsOwnerOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):

        if request.method in permissions.SAFE_METHODS:
            return True

        user = UserSerializer(request.user).data
        is_owner = Link.objects.filter(slug=view.kwargs['slug']).filter(user_id=user['id']).exists()
        return is_owner