from django.urls import path
from apps.whatsapp import views

app_name = 'whatsapp'

urlpatterns = [
    path('webhook/', views.whatsapp_webhook, name='webhook'),
    path('test/', views.send_test_message, name='test'),
]

