from django.urls import include
from django.urls import path

from rest_framework_simplejwt import views as jwt_views

from authentication.views import LogoutView
from authentication.views import LoginView
from authentication.views import csrf

app_name = 'authentication'

urlpatterns = [
    path('token/obtain/', LoginView.as_view(), name='token_create'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='api_logout'),
    path('csrf/', csrf, name='csrf'),
    path('registration/', include('dj_rest_auth.registration.urls')),
]
