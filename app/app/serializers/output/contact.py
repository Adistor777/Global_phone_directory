from rest_framework import serializers
from app.models.contact import Contact
from app.models.scam import ScamRecord


class ContactOutputSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    spam_likelihood = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = (
            'id', 
            'first_name', 
            'last_name', 
            'full_name', 
            'phone_number',
            'spam_likelihood',
            'created_at',
        )

    def get_spam_likelihood(self, obj: Contact):
        count = ScamRecord.objects.filter(phone_number=obj.phone_number).count()
        return count

    def get_full_name(self, obj: Contact):
        return obj.get_full_name()