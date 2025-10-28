from django.urls import path
from apps.customers import views

app_name = 'customers'

urlpatterns = [
    path('', views.customer_list_create, name='list-create'),
    path('<int:pk>/', views.customer_detail, name='detail'),
]

