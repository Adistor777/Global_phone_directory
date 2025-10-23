from rest_framework import serializers
from app.models.user import User


class UserOutputSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 
            'first_name', 
            'last_name', 
            'full_name', 
            'email', 
            'phone_number',
            'created_at',
        )

    def get_full_name(self, obj: User):
        return obj.get_full_name()