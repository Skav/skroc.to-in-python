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
        fields = ['id', 'original_link', 'shorted_link', 'slug', 'user_id']

class UserSerializer(serializers.ModelSerializer):
    links = serializers.PrimaryKeyRelatedField(many=True, queryset=models.Link.objects.all())

    def create(self, validated_data):
        user = User.objects.create_user(
            validated_data['username'],
            validated_data['email'],
            validated_data['password'],
        )
        user.save()

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'links', 'is_active']
        write_only_fields = ('password',)
        read_only_fields = ('id',)