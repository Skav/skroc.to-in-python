from django.urls import path
from . import views
from .views import UserViewSet
from rest_framework.urlpatterns import format_suffix_patterns

user_list = UserViewSet.as_view({
    'get': 'list'
})

user_detail = UserViewSet.as_view({
    'get': 'retrieve'
})


urlpatterns = [
    path('', views.api_root),
    path('links', views.LinkList.as_view(), name='link-list'),
    path('links/<slug:slug>', views.LinkDetail.as_view(), name='link-detail'),
    path('users', user_list, name='user-list'),
    path('users/<int:pk>', user_detail, name='user-detail'),
    path('<slug:slug>', views.LinkRedirect, name='link-redirect'),
]
