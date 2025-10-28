from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from apps.customers.models import Customer
from apps.customers.serializers import CustomerSerializer


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def customer_list_create(request):
    """List all customers or create a new one"""
    if request.method == 'GET':
        customers = Customer.objects.all()
        
        # Filter by organization
        organization_id = request.query_params.get('organization_id', None)
        if organization_id:
            customers = customers.filter(organization_id=organization_id)
        
        # Search
        search = request.query_params.get('search', None)
        if search:
            customers = customers.filter(
                Q(customer_name__icontains=search) |
                Q(phone_number__icontains=search) |
                Q(email__icontains=search)
            )
        
        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(customers, request)
        
        serializer = CustomerSerializer(result_page, many=True)
        return paginator.get_paginated_response({
            'count': paginator.page.paginator.count,
            'results': serializer.data
        })
    
    elif request.method == 'POST':
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Customer created successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def customer_detail(request, pk):
    """Get, update, or delete a customer"""
    try:
        customer = Customer.objects.get(customer_id=pk)
    except Customer.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Customer not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = CustomerSerializer(customer)
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    elif request.method == 'PUT' or request.method == 'PATCH':
        serializer = CustomerSerializer(customer, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Customer updated successfully',
                'data': serializer.data
            })
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        customer.delete()
        return Response({
            'success': True,
            'message': 'Customer deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)

