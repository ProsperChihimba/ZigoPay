from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from apps.cargo.models import Cargo, CargoHistory
from apps.cargo.serializers import CargoSerializer, CargoHistorySerializer
from apps.notifications.models import Notification
from datetime import date


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def cargo_list_create(request):
    """List all cargo or register new cargo"""
    if request.method == 'GET':
        cargo_list = Cargo.objects.all()
        
        # Filters
        status_filter = request.query_params.get('status', None)
        if status_filter:
            cargo_list = cargo_list.filter(status=status_filter)
        
        warehouse_id = request.query_params.get('warehouse_id', None)
        if warehouse_id:
            cargo_list = cargo_list.filter(warehouse_id=warehouse_id)
        
        customer_id = request.query_params.get('customer_id', None)
        if customer_id:
            cargo_list = cargo_list.filter(customer_id=customer_id)
        
        # Search
        search = request.query_params.get('search', None)
        if search:
            cargo_list = cargo_list.filter(
                Q(tracking_number__icontains=search) |
                Q(cargo_name__icontains=search)
            )
        
        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(cargo_list, request)
        
        serializer = CargoSerializer(result_page, many=True)
        return paginator.get_paginated_response({
            'count': paginator.page.paginator.count,
            'results': serializer.data
        })
    
    elif request.method == 'POST':
        data = request.data.copy()
        data['created_by'] = request.user.user_id
        
        serializer = CargoSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            
            # Create cargo history
            CargoHistory.objects.create(
                cargo=serializer.instance,
                previous_status=None,
                new_status='pending',
                updated_by=request.user,
                remarks='Cargo registered'
            )
            
            # Send notification (placeholder - will implement properly later)
            
            return Response({
                'success': True,
                'message': 'Cargo registered successfully',
                'cargo': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cargo_detail(request, pk):
    """Get cargo details"""
    try:
        cargo = Cargo.objects.get(cargo_id=pk)
    except Cargo.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Cargo not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = CargoSerializer(cargo)
    return Response({
        'success': True,
        'data': serializer.data
    })


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def cargo_update_status(request, pk):
    """Update cargo status"""
    try:
        cargo = Cargo.objects.get(cargo_id=pk)
    except Cargo.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Cargo not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    new_status = request.data.get('status')
    remarks = request.data.get('remarks', '')
    
    if not new_status:
        return Response({
            'success': False,
            'error': 'Status is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    previous_status = cargo.status
    cargo.status = new_status
    cargo.save()
    
    # Create history
    CargoHistory.objects.create(
        cargo=cargo,
        previous_status=previous_status,
        new_status=new_status,
        updated_by=request.user,
        remarks=remarks
    )
    
    # If status is 'arrived', generate invoice
    if new_status == 'arrived':
        from apps.invoices.models import Invoice
        from datetime import datetime, timedelta
        from apps.payments.utils import process_auto_payment
        
        invoice = Invoice.objects.create(
            cargo=cargo,
            amount=cargo.cargo_value * 0.3,  # 30% of cargo value as dummy invoice
            currency='USD',
            due_date=date.today() + timedelta(days=7),
            status='pending',
            created_by=request.user
        )
        
        # Check for auto-payment
        auto_payment_success, auto_payment_message, auto_payment_data = process_auto_payment(invoice, request.user)
    
    serializer = CargoSerializer(cargo)
    return Response({
        'success': True,
        'message': 'Cargo status updated successfully',
        'cargo': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cargo_history(request, pk):
    """Get cargo history"""
    try:
        cargo = Cargo.objects.get(cargo_id=pk)
    except Cargo.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Cargo not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    history = CargoHistory.objects.filter(cargo=cargo).order_by('-updated_at')
    serializer = CargoHistorySerializer(history, many=True)
    
    return Response({
        'success': True,
        'cargo_id': pk,
        'tracking_number': cargo.tracking_number,
        'history': serializer.data
    })


@api_view(['GET'])
@permission_classes([])
def public_tracking(request, tracking_number):
    """Public tracking endpoint"""
    try:
        cargo = Cargo.objects.get(tracking_number=tracking_number)
    except Cargo.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Cargo not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    history = CargoHistory.objects.filter(cargo=cargo).order_by('updated_at')
    timeline = []
    
    for h in history:
        timeline.append({
            'status': h.new_status,
            'timestamp': h.updated_at.isoformat(),
            'remarks': h.remarks
        })
    
    serializer = CargoSerializer(cargo)
    data = serializer.data
    data['timeline'] = timeline
    data['current_location'] = cargo.destination_location if cargo.status == 'arrived' else cargo.origin_location
    
    return Response({
        'success': True,
        'data': data
    })