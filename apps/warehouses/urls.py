from django.urls import path
from apps.warehouses import views

app_name = 'warehouses'

urlpatterns = [
    path('', views.warehouse_list_create, name='list-create'),
    path('<int:pk>/', views.warehouse_detail, name='detail'),
]

