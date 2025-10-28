from django.urls import path
from apps.notifications import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='list'),
    path('send/', views.send_notification, name='send'),
]

