from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from datetime import datetime
from apps.payments.models import Payment, Transaction, ReleaseOrder, Wallet, WalletTransaction
from apps.payments.serializers import PaymentSerializer, TransactionSerializer, ReleaseOrderSerializer, WalletSerializer, WalletTransactionSerializer
from apps.payments.services import PaymentGatewayService
from apps.cargo.models import Cargo
import uuid


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


def generate_release_code():
    """Generate unique release code"""
    return f"RO-{datetime.now().strftime('%y%m%d')}-{uuid.uuid4().hex[:6].upper()}"


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_list(request):
    """List all payments"""
    payments = Payment.objects.all()
    
    paginator = StandardResultsSetPagination()
    result_page = paginator.paginate_queryset(payments, request)
    
    serializer = PaymentSerializer(result_page, many=True)
    return paginator.get_paginated_response({
        'count': paginator.page.paginator.count,
        'results': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_detail(request, pk):
    """Get payment details"""
    try:
        payment = Payment.objects.get(payment_id=pk)
    except Payment.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Payment not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = PaymentSerializer(payment)
    return Response({
        'success': True,
        'data': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_payment(request):
    """Process a payment"""
    invoice_id = request.data.get('invoice_id')
    control_number = request.data.get('control_number')
    amount_paid = request.data.get('amount_paid')
    payment_method = request.data.get('payment_method', 'mobile_money')
    payment_reference = request.data.get('payment_reference')
    
    if not invoice_id or not control_number or not amount_paid:
        return Response({
            'success': False,
            'error': 'Invoice ID, control number, and amount are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    from apps.invoices.models import Invoice
    
    try:
        invoice = Invoice.objects.get(invoice_id=invoice_id, control_number=control_number)
    except Invoice.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Invalid invoice or control number'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if invoice.status == 'paid':
        return Response({
            'success': False,
            'error': 'Invoice already paid'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Create payment
    payment = Payment.objects.create(
        invoice=invoice,
        amount_paid=amount_paid,
        payment_reference=payment_reference or f"PAY-{uuid.uuid4().hex[:8].upper()}",
        payment_method=payment_method,
        status='completed',
        processed_by=request.user,
        processed_at=datetime.now()
    )
    
    # Update invoice
    invoice.status = 'paid'
    invoice.payment_method = payment_method
    invoice.save()
    
    # Create transaction
    Transaction.objects.create(
        payment=payment,
        transaction_type='cargo_payment',
        amount=amount_paid,
        currency='USD',
        status='success',
        reference=payment.payment_reference,
        created_by=request.user,
        transaction_details=request.data.get('transaction_details', {})
    )
    
    # Generate release order
    release_order = ReleaseOrder.objects.create(
        cargo=invoice.cargo,
        payment=payment,
        release_code=generate_release_code(),
        status='active',
        generated_by=request.user
    )
    
    payment_serializer = PaymentSerializer(payment)
    release_order_serializer = ReleaseOrderSerializer(release_order)
    
    return Response({
        'success': True,
        'message': 'Payment processed successfully',
        'payment': payment_serializer.data,
        'release_order': release_order_serializer.data
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def release_order_detail(request, release_code):
    """Get release order by code"""
    try:
        release_order = ReleaseOrder.objects.get(release_code=release_code)
    except ReleaseOrder.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Release order not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ReleaseOrderSerializer(release_order)
    return Response({
        'success': True,
        'data': serializer.data
    })


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def complete_release_order(request, pk):
    """Mark release order as used (cargo collected)"""
    try:
        release_order = ReleaseOrder.objects.get(release_order_id=pk)
    except ReleaseOrder.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Release order not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if release_order.status != 'active':
        return Response({
            'success': False,
            'error': 'Release order already used or expired'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    release_order.status = 'used'
    release_order.used_at = datetime.now()
    release_order.save()
    
    # Update cargo status
    cargo = release_order.cargo
    cargo.status = 'delivered'
    cargo.save()
    
    # Create cargo history
    from apps.cargo.models import CargoHistory
    CargoHistory.objects.create(
        cargo=cargo,
        previous_status='arrived',
        new_status='delivered',
        updated_by=request.user,
        remarks='Cargo collected by customer'
    )
    
    serializer = ReleaseOrderSerializer(release_order)
    return Response({
        'success': True,
        'message': 'Release order completed successfully',
        'data': serializer.data
    })


# ==================== WALLET ENDPOINTS ====================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def wallet_list_create(request):
    """List all wallets or create wallet for customer"""
    if request.method == 'GET':
        wallets = Wallet.objects.all()
        
        # Filter by customer
        customer_id = request.query_params.get('customer_id', None)
        if customer_id:
            wallets = wallets.filter(customer_id=customer_id)
        
        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(wallets, request)
        
        serializer = WalletSerializer(result_page, many=True)
        return paginator.get_paginated_response({
            'count': paginator.page.paginator.count,
            'results': serializer.data
        })
    
    elif request.method == 'POST':
        # Create wallet for customer
        customer_id = request.data.get('customer_id')
        if not customer_id:
            return Response({
                'success': False,
                'error': 'Customer ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        from apps.customers.models import Customer
        
        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Customer not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if wallet already exists
        if Wallet.objects.filter(customer=customer).exists():
            wallet = Wallet.objects.get(customer=customer)
            serializer = WalletSerializer(wallet)
            return Response({
                'success': True,
                'message': 'Wallet already exists',
                'data': serializer.data
            })
        
        wallet = Wallet.objects.create(
            customer=customer,
            auto_payment_enabled=request.data.get('auto_payment_enabled', False)
        )
        
        serializer = WalletSerializer(wallet)
        return Response({
            'success': True,
            'message': 'Wallet created successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def wallet_detail(request, pk):
    """Get wallet details or update wallet settings"""
    try:
        wallet = Wallet.objects.get(wallet_id=pk)
    except Wallet.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Wallet not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = WalletSerializer(wallet)
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    elif request.method == 'PATCH':
        # Update wallet settings (auto_payment_enabled, is_active)
        auto_payment = request.data.get('auto_payment_enabled')
        is_active = request.data.get('is_active')
        
        if auto_payment is not None:
            wallet.auto_payment_enabled = auto_payment
        if is_active is not None:
            wallet.is_active = is_active
        
        wallet.save()
        
        serializer = WalletSerializer(wallet)
        return Response({
            'success': True,
            'message': 'Wallet updated successfully',
            'data': serializer.data
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def wallet_by_customer(request, customer_id):
    """Get wallet by customer ID"""
    try:
        wallet = Wallet.objects.get(customer_id=customer_id)
    except Wallet.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Wallet not found for this customer'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = WalletSerializer(wallet)
    return Response({
        'success': True,
        'data': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def wallet_deposit(request, pk):
    """Deposit money into wallet"""
    try:
        wallet = Wallet.objects.get(wallet_id=pk)
    except Wallet.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Wallet not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    amount = request.data.get('amount')
    payment_method = request.data.get('payment_method', 'mobile_money')
    description = request.data.get('description')
    
    if not amount:
        return Response({
            'success': False,
            'error': 'Amount is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError("Amount must be positive")
    except (ValueError, TypeError):
        return Response({
            'success': False,
            'error': 'Invalid amount'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Process payment via gateway (dummy)
    success, reference, gateway_response = PaymentGatewayService.process_deposit(
        amount=amount,
        payment_method=payment_method,
        customer_phone=wallet.customer.phone_number,
        customer_email=wallet.customer.email
    )
    
    if not success:
        return Response({
            'success': False,
            'error': 'Payment gateway error'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Deposit to wallet
    try:
        balance_before = wallet.balance
        wallet.deposit(amount, reference, description)
        
        # Update transaction with gateway response
        transaction = WalletTransaction.objects.filter(
            wallet=wallet,
            reference=reference
        ).first()
        if transaction:
            transaction.gateway_response = gateway_response
            transaction.save()
        
        serializer = WalletSerializer(wallet)
        return Response({
            'success': True,
            'message': 'Deposit successful',
            'data': {
                'wallet': serializer.data,
                'deposit_amount': amount,
                'balance_before': float(balance_before),
                'balance_after': float(wallet.balance),
                'reference': reference
            }
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def wallet_withdraw(request, pk):
    """Withdraw money from wallet"""
    try:
        wallet = Wallet.objects.get(wallet_id=pk)
    except Wallet.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Wallet not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    amount = request.data.get('amount')
    description = request.data.get('description')
    
    if not amount:
        return Response({
            'success': False,
            'error': 'Amount is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError("Amount must be positive")
    except (ValueError, TypeError):
        return Response({
            'success': False,
            'error': 'Invalid amount'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Withdraw from wallet
    try:
        balance_before = wallet.balance
        reference = f"WTH-{uuid.uuid4().hex[:12].upper()}"
        wallet.withdraw(amount, reference, description)
        
        serializer = WalletSerializer(wallet)
        return Response({
            'success': True,
            'message': 'Withdrawal successful',
            'data': {
                'wallet': serializer.data,
                'withdrawal_amount': amount,
                'balance_before': float(balance_before),
                'balance_after': float(wallet.balance),
                'reference': reference
            }
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def wallet_pay_invoice(request, pk):
    """Pay invoice from wallet"""
    try:
        wallet = Wallet.objects.get(wallet_id=pk)
    except Wallet.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Wallet not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    invoice_id = request.data.get('invoice_id')
    if not invoice_id:
        return Response({
            'success': False,
            'error': 'Invoice ID is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    from apps.invoices.models import Invoice
    
    try:
        invoice = Invoice.objects.get(invoice_id=invoice_id)
    except Invoice.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Invoice not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if invoice.status == 'paid':
        return Response({
            'success': False,
            'error': 'Invoice already paid'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    amount = float(invoice.amount)
    
    # Check if wallet has sufficient balance
    if not wallet.has_sufficient_balance(amount):
        return Response({
            'success': False,
            'error': 'Insufficient wallet balance',
            'data': {
                'required': float(amount),
                'available': float(wallet.balance),
                'shortfall': float(amount - wallet.balance)
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Pay invoice from wallet
    try:
        balance_before = wallet.balance
        wallet.pay_invoice(invoice, amount)
        
        # Create payment record
        payment = Payment.objects.create(
            invoice=invoice,
            amount_paid=amount,
            payment_reference=f"WLT-{uuid.uuid4().hex[:8].upper()}",
            payment_method='wallet',
            status='completed',
            processed_by=request.user,
            processed_at=datetime.now()
        )
        
        # Update wallet transaction with payment reference
        transaction = WalletTransaction.objects.filter(
            wallet=wallet,
            invoice=invoice,
            transaction_type='payment'
        ).order_by('-created_at').first()
        if transaction:
            transaction.payment = payment
            transaction.save()
        
        # Update invoice
        invoice.status = 'paid'
        invoice.payment_method = 'wallet'
        invoice.save()
        
        # Create transaction record
        Transaction.objects.create(
            payment=payment,
            transaction_type='cargo_payment',
            amount=amount,
            currency='USD',
            status='success',
            reference=payment.payment_reference,
            created_by=request.user
        )
        
        # Generate release order
        release_order = ReleaseOrder.objects.create(
            cargo=invoice.cargo,
            payment=payment,
            release_code=generate_release_code(),
            status='active',
            generated_by=request.user
        )
        
        wallet_serializer = WalletSerializer(wallet)
        payment_serializer = PaymentSerializer(payment)
        release_order_serializer = ReleaseOrderSerializer(release_order)
        
        return Response({
            'success': True,
            'message': 'Invoice paid successfully from wallet',
            'data': {
                'wallet': wallet_serializer.data,
                'payment': payment_serializer.data,
                'release_order': release_order_serializer.data,
                'balance_before': float(balance_before),
                'balance_after': float(wallet.balance)
            }
        }, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def wallet_transactions(request, pk):
    """Get wallet transaction history"""
    try:
        wallet = Wallet.objects.get(wallet_id=pk)
    except Wallet.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Wallet not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    transactions = WalletTransaction.objects.filter(wallet=wallet).order_by('-created_at')
    
    # Filter by transaction type
    transaction_type = request.query_params.get('transaction_type', None)
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
    
    paginator = StandardResultsSetPagination()
    result_page = paginator.paginate_queryset(transactions, request)
    
    serializer = WalletTransactionSerializer(result_page, many=True)
    return paginator.get_paginated_response({
        'count': paginator.page.paginator.count,
        'results': serializer.data
    })

