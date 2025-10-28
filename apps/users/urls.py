from django.urls import path
from apps.users import views

app_name = 'users'

urlpatterns = [
    path('', views.user_list_create, name='list-create'),
    path('<int:pk>/', views.user_detail, name='detail'),
]

