from django.urls import path
from apps.invoices import views

app_name = 'invoices'

urlpatterns = [
    path('', views.invoice_list, name='list'),
    path('<int:pk>/', views.invoice_detail, name='detail'),
    path('generate/', views.generate_invoice, name='generate'),
]

