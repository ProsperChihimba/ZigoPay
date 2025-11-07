from django.urls import path
from apps.payments import views

app_name = 'payments'

urlpatterns = [
    path('', views.payment_list, name='list'),
    path('<int:pk>/', views.payment_detail, name='detail'),
    path('process/', views.process_payment, name='process'),
    path('release-orders/<str:release_code>/', views.release_order_detail, name='release-order-detail'),
    path('release-orders/<int:pk>/complete/', views.complete_release_order, name='complete-release-order'),
    
    # Wallet endpoints
    path('wallets/', views.wallet_list_create, name='wallet-list-create'),
    path('wallets/<int:pk>/', views.wallet_detail, name='wallet-detail'),
    path('wallets/customer/<int:customer_id>/', views.wallet_by_customer, name='wallet-by-customer'),
    path('wallets/<int:pk>/deposit/', views.wallet_deposit, name='wallet-deposit'),
    path('wallets/<int:pk>/withdraw/', views.wallet_withdraw, name='wallet-withdraw'),
    path('wallets/<int:pk>/pay-invoice/', views.wallet_pay_invoice, name='wallet-pay-invoice'),
    path('wallets/<int:pk>/transactions/', views.wallet_transactions, name='wallet-transactions'),
]

