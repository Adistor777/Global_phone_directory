from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from app.models import User
from app.serializers.input.user import CreateUserInputSerializer, LoginUserInputSerializer
from app.serializers.output.user import UserOutputSerializer


class UserSignupView(APIView):
    authentication_classes = []  # Disable authentication
    permission_classes = []      # Disable permissions
    
    def post(self, request):
        print("=" * 50)
        print("Signup Request Received")
        print("Data:", request.data)
        print("=" * 50)
        
        serializer = CreateUserInputSerializer(data=request.data)
        
        if serializer.is_valid():
            print("Validation passed, creating user...")
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user': UserOutputSerializer(user).data,
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
            }, status=status.HTTP_201_CREATED)
        
        print("Validation FAILED")
        print("Errors:", serializer.errors)
        print("=" * 50)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    authentication_classes = []  # Disable authentication
    permission_classes = []      # Disable permissions
    
    def post(self, request):
        serializer = LoginUserInputSerializer(data=request.data)
        
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            password = serializer.validated_data['password']
            
            # Try to authenticate existing user
            user = authenticate(request, username=phone_number, password=password)
            
            if user:
                # User exists and password is correct
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    'user': UserOutputSerializer(user).data,
                    'access_token': str(refresh.access_token),
                    'refresh_token': str(refresh),
                }, status=status.HTTP_200_OK)
            
            # Check if user exists but password is wrong
            if User.objects.filter(phone_number=phone_number).exists():
                return Response({
                    'error': 'Invalid credentials'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # User doesn't exist - auto-create with additional fields
            first_name = serializer.validated_data.get('first_name')
            last_name = serializer.validated_data.get('last_name', '')
            email = serializer.validated_data.get('email')
            
            if not first_name:
                return Response({
                    'error': 'First name required for new account creation'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create new user
            user = User.objects.create_user(
                phone_number=phone_number,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email
            )
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user': UserOutputSerializer(user).data,
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)