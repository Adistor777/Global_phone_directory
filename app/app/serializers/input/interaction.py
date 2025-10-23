from rest_framework import serializers


class CreateInteractionInputSerializer(serializers.Serializer):
    receiver_phone = serializers.CharField(required=True, max_length=20, min_length=10)
    interaction_type = serializers.ChoiceField(
        choices=['call', 'message', 'spam_report'],
        required=True
    )
    metadata = serializers.JSONField(required=False, default=dict)
    
    def validate_receiver_phone(self, value):
        from app.utils import normalize_phone_number
        try:
            return normalize_phone_number(value)
        except ValueError as e:
            raise serializers.ValidationError(str(e))