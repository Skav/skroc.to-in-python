from django.urls import path
from . import views
from .views import UserViewSet
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

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
    path('register', views.Register.as_view(), name='user-register'),
    path('login', TokenObtainPairView.as_view(), name="Token_pair_view"),
    path('login/refresh', TokenRefreshView.as_view(), name='Token_refresh'),
    path('activate', views.ActivateAccount.as_view(), name='activate_account'),
    path('reedem', views.ReedemPassword.as_view(), name='reedem_password'),
    path('<slug:slug>', views.link_redirect, name='link-redirect'),
]
