from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from apps.organizations.models import Organization
from apps.organizations.serializers import OrganizationSerializer


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def organization_list_create(request):
    """List all organizations or create a new one"""
    if request.method == 'GET':
        organizations = Organization.objects.all()
        
        # Search functionality
        search = request.query_params.get('search', None)
        if search:
            organizations = organizations.filter(
                Q(name__icontains=search) |
                Q(address__icontains=search)
            )
        
        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(organizations, request)
        
        serializer = OrganizationSerializer(result_page, many=True)
        return paginator.get_paginated_response({
            'count': paginator.page.paginator.count,
            'results': serializer.data
        })
    
    elif request.method == 'POST':
        serializer = OrganizationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Organization created successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def organization_detail(request, pk):
    """Get, update, or delete an organization"""
    try:
        organization = Organization.objects.get(organization_id=pk)
    except Organization.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Organization not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = OrganizationSerializer(organization)
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    elif request.method == 'PUT' or request.method == 'PATCH':
        serializer = OrganizationSerializer(organization, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Organization updated successfully',
                'data': serializer.data
            })
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        organization.delete()
        return Response({
            'success': True,
            'message': 'Organization deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)

