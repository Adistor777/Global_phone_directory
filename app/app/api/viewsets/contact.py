from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db import transaction, IntegrityError

from app.models import Contact, Interaction
from app.serializers.input.contact import CreateContactInputSerializer
from app.serializers.output.contact import ContactOutputSerializer


class ContactView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get all contacts for current user"""
        contacts = Contact.objects.filter(created_by=request.user).order_by('-created_at')
        serializer = ContactOutputSerializer(contacts, many=True)
        return Response(serializer.data)
    
    @transaction.atomic
    def post(self, request):
        """Create a new contact"""
        print("=" * 50)
        print("Contact Creation Request")
        print("User:", request.user.phone_number)
        print("Data:", request.data)
        print("=" * 50)
        
        # Add request to context for validation
        serializer = CreateContactInputSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            try:
                # Create contact
                contact = serializer.save(created_by=request.user)
                
                # Create interaction record (audit trail)
                Interaction.objects.create(
                    initiator=request.user,
                    receiver_phone=contact.phone_number,
                    interaction_type='contact_added',
                    metadata={
                        'contact_id': str(contact.id),
                        'contact_name': f"{contact.first_name} {contact.last_name}".strip()
                    }
                )
                
                print("✅ Contact created successfully:", contact.phone_number)
                print("=" * 50)
                
                return Response(
                    ContactOutputSerializer(contact).data,
                    status=status.HTTP_201_CREATED
                )
            
            except IntegrityError as e:
                print("❌ IntegrityError:", str(e))
                error_msg = str(e).lower()
                if 'unique' in error_msg or 'duplicate' in error_msg:
                    return Response(
                        {'error': 'You already have a contact with this phone number'},
                        status=status.HTTP_409_CONFLICT
                    )
                return Response(
                    {'error': 'Database error occurred'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            except Exception as e:
                print("❌ Error creating contact:", str(e))
                print("=" * 50)
                return Response(
                    {'error': f'Failed to create contact: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        print("❌ Validation errors:", serializer.errors)
        print("=" * 50)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)