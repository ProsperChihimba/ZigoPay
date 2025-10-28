from django.urls import path
from apps.authentication import views

app_name = 'authentication'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('refresh/', views.refresh_token_view, name='refresh'),
    path('logout/', views.logout_view, name='logout'),
]

