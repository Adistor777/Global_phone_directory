from rest_framework import serializers
from app.models.interaction import Interaction
from app.serializers.output.user import UserOutputSerializer


class InteractionOutputSerializer(serializers.ModelSerializer):
    initiator = UserOutputSerializer(read_only=True)
    receiver = UserOutputSerializer(read_only=True)
    
    class Meta:
        model = Interaction
        fields = (
            'id',
            'initiator',
            'receiver',
            'receiver_phone',
            'interaction_type',
            'metadata',
            'created_at',
        )


class TopContactOutputSerializer(serializers.Serializer):
    contact_phone = serializers.CharField()
    contact_name = serializers.CharField()
    interaction_count = serializers.IntegerField()
    is_registered = serializers.BooleanField()


class SpamStatsOutputSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    spam_count = serializers.IntegerField()
    reported_by_users = serializers.ListField()