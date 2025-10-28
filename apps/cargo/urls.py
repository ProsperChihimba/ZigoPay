from django.urls import path
from apps.cargo import views

app_name = 'cargo'

urlpatterns = [
    path('', views.cargo_list_create, name='list-create'),
    path('<int:pk>/', views.cargo_detail, name='detail'),
    path('<int:pk>/status/', views.cargo_update_status, name='update-status'),
    path('<int:pk>/history/', views.cargo_history, name='history'),
    path('track/<str:tracking_number>/', views.public_tracking, name='public-tracking'),
]