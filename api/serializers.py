from rest_framework import serializers
from .models import User, Business, Product


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'business', 'role', 'first_name', 'last_name']
        read_only_fields = ['id']


class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    business_name = serializers.CharField(source='business.name', read_only=True)
    image = serializers.ImageField(required=False)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'image', 'status', 'created_by', 'business', 'created_at', 'created_by_username', 'business_name']
        read_only_fields = ['id', 'created_at', 'created_by', 'business', 'created_by_username', 'business_name']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
