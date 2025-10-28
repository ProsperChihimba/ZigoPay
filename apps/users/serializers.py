from rest_framework import serializers
from apps.users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.warehouse_name', read_only=True, allow_null=True)
    
    class Meta:
        model = User
        fields = ['user_id', 'full_name', 'username', 'email', 'phone_number', 
                  'role', 'is_active', 'organization_id', 'warehouse_id',
                  'organization_name', 'warehouse_name', 'created_at']
        read_only_fields = ['user_id', 'created_at']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

