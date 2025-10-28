from django.urls import path
from apps.organizations import views

app_name = 'organizations'

urlpatterns = [
    path('', views.organization_list_create, name='list-create'),
    path('<int:pk>/', views.organization_detail, name='detail'),
]

