from rest_framework import serializers


class CreateScamRecordInputSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True, max_length=20, min_length=10)
    description = serializers.CharField(required=False, allow_blank=True, max_length=500, default='')
    
    def validate_phone_number(self, value):
        from app.utils import normalize_phone_number
        try:
            return normalize_phone_number(value)
        except ValueError as e:
            raise serializers.ValidationError(str(e))