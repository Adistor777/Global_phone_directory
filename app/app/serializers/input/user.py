from rest_framework import serializers
from app.models import User


class CreateUserInputSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True, min_length=5)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True)
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)

    def validate_phone_number(self, value):
        from app.utils import normalize_phone_number
        
        try:
            normalized = normalize_phone_number(value)
        except Exception as e:
            raise serializers.ValidationError(f"Invalid phone number format: {str(e)}")
        
        # Check if phone already exists
        if User.objects.filter(phone_number=normalized).exists():
            raise serializers.ValidationError("A user with this phone number already exists")
        
        return normalized

    def create(self, validated_data):
        # Extract data with safe defaults
        phone_number = validated_data['phone_number']
        password = validated_data['password']
        first_name = validated_data['first_name']
        last_name = validated_data.get('last_name') or ''
        email = validated_data.get('email') or None
        
        # Create user using the custom user manager
        user = User.objects.create_user(
            phone_number=phone_number,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email
        )
        
        return user


class LoginUserInputSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=100, required=False)
    last_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)

    def validate_phone_number(self, value):
        from app.utils import normalize_phone_number
        
        try:
            return normalize_phone_number(value)
        except Exception as e:
            raise serializers.ValidationError(f"Invalid phone number format: {str(e)}")