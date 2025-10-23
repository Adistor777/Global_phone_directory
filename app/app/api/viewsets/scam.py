from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from app.serializers import input, output
from app.models.scam import ScamRecord
from app.models.interaction import Interaction
from app.models.user import User
from django.db import transaction


class CreateScamRecord(APIView):
    """
    POST /api/spam
    Report a phone number as spam
    """
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    input_serializer_class = input.CreateScamRecordInputSerializer
    output_serializer_class = output.ScamRecordOutputSerializer

    def post(self, request):
        input_serializer = self.input_serializer_class(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        user = request.user
        
        with transaction.atomic():
            try:
                scam = ScamRecord.objects.create(
                    reported_by=user,
                    created_by=user,
                    updated_by=user,
                    **input_serializer.validated_data
                )
                
                # Track spam report interaction
                receiver_user = User.objects.filter(
                    phone_number=scam.phone_number
                ).first()
                
                Interaction.objects.create(
                    initiator=user,
                    receiver=receiver_user,
                    receiver_phone=scam.phone_number,
                    interaction_type='spam_report',
                    metadata={'description': scam.description}
                )
                
                output_serializer = self.output_serializer_class(scam)
                return Response(output_serializer.data, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )