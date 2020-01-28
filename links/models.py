from django.db import models as model
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone

class Link(model.Model):
    original_link = model.CharField(max_length=255)
    shorted_link = model.CharField(max_length=255)
    slug = model.CharField(max_length=10)
    user_id = model.ForeignKey('auth.User', related_name='links', on_delete=model.DO_NOTHING)
    created_at = model.DateTimeField(auto_now_add=True)
    updated_at = model.DateTimeField(auto_now_add=True)


class ActivateCode(model.Model):
    activation_code = model.CharField(max_length=64)
    code_type = model.CharField(max_length=10, choices=[('a', 'activate'), ['r', 'remind']], default='a')
    user = model.ForeignKey('auth.User', related_name='activate', on_delete=model.CASCADE)
    created_at = model.DateTimeField(default=timezone.now())
    updated_at = model.DateTimeField(default=timezone.now())
    expires_at = model.DateTimeField(default=timezone.now()+timedelta(hours=1))
    is_active = model.BooleanField(default=True)