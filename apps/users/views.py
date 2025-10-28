from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from apps.users.models import User
from apps.users.serializers import UserSerializer


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def user_list_create(request):
    """List all users or create a new one"""
    if request.method == 'GET':
        users = User.objects.all()
        
        # Filter by organization
        organization_id = request.query_params.get('organization_id', None)
        if organization_id:
            users = users.filter(organization_id=organization_id)
        
        # Filter by warehouse
        warehouse_id = request.query_params.get('warehouse_id', None)
        if warehouse_id:
            users = users.filter(warehouse_id=warehouse_id)
        
        # Filter by role
        role = request.query_params.get('role', None)
        if role:
            users = users.filter(role=role)
        
        # Search
        search = request.query_params.get('search', None)
        if search:
            users = users.filter(
                Q(full_name__icontains=search) |
                Q(username__icontains=search) |
                Q(email__icontains=search)
            )
        
        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(users, request)
        
        serializer = UserSerializer(result_page, many=True)
        return paginator.get_paginated_response({
            'count': paginator.page.paginator.count,
            'results': serializer.data
        })
    
    elif request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'User created successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def user_detail(request, pk):
    """Get, update, or delete a user"""
    try:
        user = User.objects.get(user_id=pk)
    except User.DoesNotExist:
        return Response({
            'success': False,
            'error': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    elif request.method == 'PUT' or request.method == 'PATCH':
        serializer = UserSerializer(user, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'User updated successfully',
                'data': serializer.data
            })
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        user.delete()
        return Response({
            'success': True,
            'message': 'User deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)

