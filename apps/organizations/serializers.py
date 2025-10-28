from rest_framework import serializers
from apps.organizations.models import Organization


class OrganizationSerializer(serializers.ModelSerializer):
    """Serializer for Organization model"""
    
    class Meta:
        model = Organization
        fields = ['organization_id', 'name', 'address', 'contact_phone', 
                  'contact_email', 'status', 'created_at', 'updated_at']
        read_only_fields = ['organization_id', 'created_at', 'updated_at']

