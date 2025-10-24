from rest_framework import serializers
from app.models import Contact
from app.utils import normalize_phone_number


class CreateContactInputSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100, required=False, allow_blank=True)

    def validate_phone_number(self, value):
        """Normalize and validate phone number"""
        try:
            normalized = normalize_phone_number(value)
            
            # Check if contact already exists for this user
            user = self.context.get('request').user if self.context.get('request') else None
            if user and Contact.objects.filter(phone_number=normalized, created_by=user).exists():
                raise serializers.ValidationError("You already have a contact with this phone number")
            
            return normalized
        except Exception as e:
            raise serializers.ValidationError(str(e))

    def create(self, validated_data):
        """
        Create the contact instance
        THIS METHOD WAS MISSING - CRITICAL FIX
        """
        return Contact.objects.create(**validated_data)