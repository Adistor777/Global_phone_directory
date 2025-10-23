from rest_framework import serializers


class CreateContactInputSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True, max_length=50)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=50, default='')
    phone_number = serializers.CharField(required=True, max_length=20, min_length=10)
    
    def validate_phone_number(self, value):
        from app.utils import normalize_phone_number
        try:
            return normalize_phone_number(value)
        except ValueError as e:
            raise serializers.ValidationError(str(e))