from rest_framework import serializers
from . import models
from django.contrib.auth.models import User

class LinkSerializer(serializers.ModelSerializer):
    user_id = serializers.ReadOnlyField(source='user_id.id')

    def validate(self, data):
        original_link = data['original_link']
        shorted_link = data['shorted_link']
        slug = data['slug']
        if original_link.find('.') == -1:
            raise serializers.ValidationError('Link doesn\'t have a dot')
        if shorted_link.find(slug) == -1:
            raise serializers.ValidationError('Different slug in link than slug')

        return data


    class Meta:
        model = models.Link
        fields = ('id', 'original_link', 'shorted_link', 'slug', 'user_id')

class UserSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        user = User.objects.create_user(
            validated_data['username'],
            validated_data['email'],
            validated_data['password'],
        )
        user.is_active = False
        user.save()

        return user

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email', 'is_active')
        read_only_fields = ('id', 'is_staff', 'is_superuser')
        extra_kwargs = {
            'password': {
                'write_only': True,
            },
            'is_active': {
                'write_only': True
            }
        }


class ActivateCodeSerializer(serializers.ModelSerializer):
    user_id = serializers.ReadOnlyField(source='user.id')

    class Meta:
        model = models.ActivateCode
        fields = ('id', 'activation_code', 'code_type', 'user_id', 'created_at', 'expires_at', 'is_active')
        read_only_fields = ('id',)