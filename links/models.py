from django.db import models as model
from django.contrib.auth.models import User

class Link(model.Model):
    original_link = model.CharField(max_length=255)
    shorted_link = model.CharField(max_length=255)
    slug = model.CharField(max_length=10)
    user_id = model.ForeignKey('auth.User', related_name='links', on_delete=model.DO_NOTHING)
    created_at = model.DateTimeField(auto_now_add=True)
    updated_at = model.DateTimeField(auto_now_add=True)