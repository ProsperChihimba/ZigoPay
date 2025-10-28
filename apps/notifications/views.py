from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from apps.notifications.models import Notification
from apps.notifications.serializers import NotificationSerializer
from apps.customers.models import Customer


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_list(request):
    """List all notifications"""
    notifications = Notification.objects.all()
    
    # Filter by customer
    customer_id = request.query_params.get('customer_id', None)
    if customer_id:
        notifications = notifications.filter(customer_id=customer_id)
    
    # Filter by cargo
    cargo_id = request.query_params.get('cargo_id', None)
    if cargo_id:
        notifications = notifications.filter(cargo_id=cargo_id)
    
    paginator = StandardResultsSetPagination()
    result_page = paginator.paginate_queryset(notifications, request)
    
    serializer = NotificationSerializer(result_page, many=True)
    return paginator.get_paginated_response({
        'count': paginator.page.paginator.count,
        'results': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_notification(request):
    """Send a notification"""
    customer_id = request.data.get('customer_id')
    cargo_id = request.data.get('cargo_id')
    notification_type = request.data.get('notification_type')
    content = request.data.get('content')
    delivery_method = request.data.get('delivery_method', 'whatsapp')
    
    if not customer_id or not notification_type or not content:
        return Response({
            'success': False,
            'error': 'Customer ID, notification type, and content are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        customer = Customer.objects.get(customer_id=customer_id)
    except Customer.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Customer not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Create notification (dummy implementation - will integrate with actual SMS/WhatsApp/Email later)
    notification = Notification.objects.create(
        customer=customer,
        cargo_id=cargo_id if cargo_id else None,
        notification_type=notification_type,
        delivery_method=delivery_method,
        content=content,
        status='sent',
        sent_by=request.user
    )
    
    # TODO: Actually send notification via SMS/WhatsApp/Email
    # For now, just log it
    
    serializer = NotificationSerializer(notification)
    return Response({
        'success': True,
        'message': 'Notification sent successfully',
        'data': serializer.data
    }, status=status.HTTP_201_CREATED)

