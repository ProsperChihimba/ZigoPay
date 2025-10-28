from django.urls import path
from apps.payments import views

app_name = 'payments'

urlpatterns = [
    path('', views.payment_list, name='list'),
    path('<int:pk>/', views.payment_detail, name='detail'),
    path('process/', views.process_payment, name='process'),
    path('release-orders/<str:release_code>/', views.release_order_detail, name='release-order-detail'),
    path('release-orders/<int:pk>/complete/', views.complete_release_order, name='complete-release-order'),
]

