from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from datetime import datetime, timedelta
from apps.invoices.models import Invoice, StorageFee
from apps.invoices.serializers import InvoiceSerializer, StorageFeeSerializer


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def invoice_list(request):
    """List all invoices"""
    invoices = Invoice.objects.all()
    
    # Filters
    status_filter = request.query_params.get('status', None)
    if status_filter:
        invoices = invoices.filter(status=status_filter)
    
    cargo_id = request.query_params.get('cargo_id', None)
    if cargo_id:
        invoices = invoices.filter(cargo_id=cargo_id)
    
    paginator = StandardResultsSetPagination()
    result_page = paginator.paginate_queryset(invoices, request)
    
    serializer = InvoiceSerializer(result_page, many=True)
    return paginator.get_paginated_response({
        'count': paginator.page.paginator.count,
        'results': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def invoice_detail(request, pk):
    """Get invoice details"""
    try:
        invoice = Invoice.objects.get(invoice_id=pk)
    except Invoice.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Invoice not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = InvoiceSerializer(invoice)
    return Response({
        'success': True,
        'data': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_invoice(request):
    """Generate invoice for cargo"""
    cargo_id = request.data.get('cargo_id')
    amount = request.data.get('amount')
    
    if not cargo_id or not amount:
        return Response({
            'success': False,
            'error': 'Cargo ID and amount are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    from apps.cargo.models import Cargo
    
    try:
        cargo = Cargo.objects.get(cargo_id=cargo_id)
    except Cargo.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Cargo not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    invoice = Invoice.objects.create(
        cargo=cargo,
        amount=amount,
        currency='USD',
        due_date=datetime.now().date() + timedelta(days=7),
        status='pending',
        created_by=request.user
    )
    
    serializer = InvoiceSerializer(invoice)
    return Response({
        'success': True,
        'message': 'Invoice generated successfully',
        'data': serializer.data
    }, status=status.HTTP_201_CREATED)

