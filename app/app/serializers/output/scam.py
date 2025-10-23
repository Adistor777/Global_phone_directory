from rest_framework import serializers
from app.models.scam import ScamRecord
from app.serializers.output.user import UserOutputSerializer


class ScamRecordOutputSerializer(serializers.ModelSerializer):
    reported_by = UserOutputSerializer(read_only=True)
    spam_likelihood = serializers.SerializerMethodField()
    
    class Meta:
        model = ScamRecord
        fields = (
            'id',
            'phone_number',
            'spam_likelihood',
            'description',
            'reported_by',
            'created_at',
            'updated_at'
        )

    def get_spam_likelihood(self, obj: ScamRecord):
        return ScamRecord.objects.filter(phone_number=obj.phone_number).count()