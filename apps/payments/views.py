from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from datetime import datetime
from apps.payments.models import Payment, Transaction, ReleaseOrder
from apps.payments.serializers import PaymentSerializer, TransactionSerializer, ReleaseOrderSerializer
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

