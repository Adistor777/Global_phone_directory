from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from app.serializers.input.contact import CreateContactInputSerializer  # FIXED
from app.serializers.output.contact import ContactOutputSerializer

class ContactView(APIView):
    """
    API endpoint to create a new contact
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateContactInputSerializer(data=request.data, context={'request': request})  # FIXED
        
        if serializer.is_valid():
            contact = serializer.save(created_by=request.user)
            output_serializer = ContactOutputSerializer(contact)
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)