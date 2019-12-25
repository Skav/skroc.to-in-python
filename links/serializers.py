from rest_framework import serializers
from . import models
from django.contrib.auth.models import User

class LinkSerializer(serializers.ModelSerializer):
    user_id = serializers.ReadOnlyField(source='user_id.username')

    class Meta:
        model = models.Link
        fields = ['id', 'original_link', 'shorted_link', 'slug', 'user_id']

class UserSerializer(serializers.ModelSerializer):
    links = serializers.PrimaryKeyRelatedField(many=True, queryset=models.Link.objects.all())

    class Meta:
        model = User
        fields = ['id', 'username', 'links']