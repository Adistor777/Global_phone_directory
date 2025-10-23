from rest_framework import serializers
from app.models.user import User
from app.models.contact import Contact
from app.models.scam import ScamRecord


class SearchOutputSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.SerializerMethodField()
    phone_number = serializers.CharField()
    is_registered = serializers.SerializerMethodField()
    spam_likelihood = serializers.SerializerMethodField()
    match_score = serializers.IntegerField(required=False, default=0)

    def get_name(self, obj):
        if isinstance(obj, User) or isinstance(obj, Contact):
            return obj.get_full_name()
        return ""

    def get_is_registered(self, obj):
        return isinstance(obj, User)

    def get_spam_likelihood(self, obj):
        if isinstance(obj, User) or isinstance(obj, Contact):
            phone_number = obj.phone_number
            return ScamRecord.objects.filter(phone_number=phone_number).count()
        return 0


class SearchDetailsUserOutputSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    spam_likelihood = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 
            'first_name', 
            'last_name', 
            'full_name', 
            'phone_number',
            'email',
            'spam_likelihood',
        )

    def get_spam_likelihood(self, obj: User):
        return ScamRecord.objects.filter(phone_number=obj.phone_number).count()

    def get_full_name(self, obj: User):
        return obj.get_full_name()
    
    def get_email(self, obj: User):
        # Only show email if the requesting user has this person in their contacts
        request = self.context.get('request')
        if request and request.user:
            from app.models.contact import Contact
            is_in_contacts = Contact.objects.filter(
                created_by=request.user,
                phone_number=obj.phone_number
            ).exists()
            return obj.email if is_in_contacts else None
        return None


class SearchDetailsContactOutputSerializer(serializers.ModelSerializer):
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
        )

    def get_spam_likelihood(self, obj: Contact):
        return ScamRecord.objects.filter(phone_number=obj.phone_number).count()

    def get_full_name(self, obj: Contact):
        return obj.get_full_name()