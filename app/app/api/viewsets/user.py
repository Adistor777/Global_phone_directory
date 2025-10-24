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
            print("✅ Validation passed, creating user...")
            try:
                user = serializer.save()
                refresh = RefreshToken.for_user(user)
                
                response_data = {
                    'user': UserOutputSerializer(user).data,
                    'access_token': str(refresh.access_token),
                    'refresh_token': str(refresh),
                }
                
                print("✅ SUCCESS! User created:", user.phone_number)
                return Response(response_data, status=status.HTTP_201_CREATED)
            
            except Exception as e:
                print("❌ Error creating user:", str(e))
                return Response(
                    {'error': f'Failed to create user: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        print("❌ Validation FAILED")
        print("Errors:", serializer.errors)
        print("=" * 50)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    authentication_classes = []  # Disable authentication
    permission_classes = []      # Disable permissions
    
    def post(self, request):
        print("=" * 50)
        print("Login Request Received")
        print("Data:", {**request.data, 'password': '***'})  # Hide password in logs
        print("=" * 50)
        
        serializer = LoginUserInputSerializer(data=request.data)
        
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            password = serializer.validated_data['password']
            
            # Try to authenticate existing user
            user = authenticate(request, username=phone_number, password=password)
            
            if user:
                # ✅ Existing user with correct password
                print("✅ User authenticated successfully:", phone_number)
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    'user': UserOutputSerializer(user).data,
                    'access_token': str(refresh.access_token),
                    'refresh_token': str(refresh),
                }, status=status.HTTP_200_OK)
            
            # Check if user exists (for better error message)
            if User.objects.filter(phone_number=phone_number).exists():
                # ✅ User exists but wrong password
                print("❌ Invalid password for:", phone_number)
                return Response({
                    'error': 'Invalid credentials. Please check your password.'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # ✅ User doesn't exist - auto-create IF first_name provided
            first_name = serializer.validated_data.get('first_name')
            
            if not first_name:
                # User doesn't exist and no first_name = can't auto-create
                print("❌ User not found and no first_name for auto-create:", phone_number)
                return Response({
                    'error': 'Account not found. Please sign up first or provide your name to create an account.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Auto-create new user
            print("✅ Auto-creating new user:", phone_number)
            last_name = serializer.validated_data.get('last_name', '')
            email = serializer.validated_data.get('email')
            
            try:
                user = User.objects.create_user(
                    phone_number=phone_number,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    email=email
                )
                
                refresh = RefreshToken.for_user(user)
                print("✅ New user created successfully:", phone_number)
                
                return Response({
                    'user': UserOutputSerializer(user).data,
                    'access_token': str(refresh.access_token),
                    'refresh_token': str(refresh),
                }, status=status.HTTP_201_CREATED)
            
            except Exception as e:
                print("❌ Error auto-creating user:", str(e))
                return Response({
                    'error': f'Failed to create account: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        print("❌ Validation FAILED")
        print("Errors:", serializer.errors)
        print("=" * 50)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)