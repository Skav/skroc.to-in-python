from django.urls import path
from . import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('links', views.LinkList.as_view()),
    path('links/<slug:slug>', views.LinkDetail.as_view()),
    path('users', views.UserList.as_view()),
    path('users/<int:pk>', views.UserDetail.as_view())
]