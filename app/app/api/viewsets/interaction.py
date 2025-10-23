from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count, Q
from datetime import datetime, timedelta
from app.models.interaction import Interaction
from app.models.scam import ScamRecord
from app.models import User
from app.serializers.input.interaction import CreateInteractionInputSerializer
from app.serializers.output.interaction import InteractionOutputSerializer


class InteractionView(APIView):
    """
    API endpoint to create a new interaction
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateInteractionInputSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            interaction = serializer.save(initiator=request.user)
            output_serializer = InteractionOutputSerializer(interaction)
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RecentInteractionsView(APIView):
    """
    API endpoint to retrieve recent interactions for authenticated user
    Supports pagination and filtering by interaction type
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get query parameters
        interaction_type = request.query_params.get('type')
        
        # Base queryset - user's interactions
        queryset = Interaction.objects.filter(
            initiator=request.user
        ).select_related('initiator', 'receiver').order_by('-created_at')
        
        # Filter by type if specified
        if interaction_type:
            if interaction_type not in ['call', 'message', 'spam_report']:
                return Response(
                    {'error': 'Invalid interaction type. Must be: call, message, or spam_report'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            queryset = queryset.filter(interaction_type=interaction_type)
        
        # Paginate results
        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        
        # Serialize
        serializer = InteractionOutputSerializer(paginated_queryset, many=True)
        
        return paginator.get_paginated_response(serializer.data)


class TopContactsView(APIView):
    """
    API endpoint to get user's most frequently contacted people
    Returns top N contacts with interaction counts
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get limit from query params (default 5, max 50)
        try:
            limit = int(request.query_params.get('limit', 5))
            limit = min(limit, 50)  # Cap at 50
        except ValueError:
            return Response(
                {'error': 'Invalid limit parameter. Must be an integer.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Aggregate interactions by contact
        top_contacts = Interaction.objects.filter(
            initiator=request.user
        ).values('receiver_phone').annotate(
            interaction_count=Count('id')
        ).order_by('-interaction_count')[:limit]
        
        # Enrich with contact details
        results = []
        for contact in top_contacts:
            phone = contact['receiver_phone']
            count = contact['interaction_count']
            
            # Try to find registered user first
            user = User.objects.filter(phone_number=phone).first()
            if user:
                results.append({
                    'contact_name': user.get_full_name(),
                    'contact_phone': phone,
                    'interaction_count': count,
                    'is_registered': True
                })
            else:
                # Check if it's in user's contacts
                from app.models.contact import Contact
                contact_obj = Contact.objects.filter(
                    created_by=request.user,
                    phone_number=phone
                ).first()
                
                if contact_obj:
                    name = f"{contact_obj.first_name} {contact_obj.last_name}".strip()
                else:
                    name = phone
                
                results.append({
                    'contact_name': name,
                    'contact_phone': phone,
                    'interaction_count': count,
                    'is_registered': False
                })
        
        return Response(results)


class SpamStatsView(APIView):
    """
    API endpoint to get aggregated spam statistics
    Supports filtering by date range and minimum report count
    
    Query Parameters:
    - start_date: ISO format (YYYY-MM-DD) - Filter reports from this date
    - end_date: ISO format (YYYY-MM-DD) - Filter reports until this date
    - min_reports: Integer - Only show numbers with at least this many reports
    - phone_number: String - Get stats for specific phone number only
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Base queryset
        queryset = ScamRecord.objects.all()
        
        # Filter by specific phone number if provided
        phone_number = request.query_params.get('phone_number')
        if phone_number:
            from app.utils import normalize_phone_number
            try:
                normalized_phone = normalize_phone_number(phone_number)
                queryset = queryset.filter(phone_number=normalized_phone)
            except Exception as e:
                return Response(
                    {'error': f'Invalid phone number: {str(e)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Filter by date range if provided
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            try:
                start = datetime.fromisoformat(start_date)
                queryset = queryset.filter(created_at__gte=start)
            except ValueError:
                return Response(
                    {'error': 'Invalid start_date format. Use ISO format (YYYY-MM-DD)'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if end_date:
            try:
                # Add 23:59:59 to include the entire end date
                end = datetime.fromisoformat(end_date)
                end = end.replace(hour=23, minute=59, second=59)
                queryset = queryset.filter(created_at__lte=end)
            except ValueError:
                return Response(
                    {'error': 'Invalid end_date format. Use ISO format (YYYY-MM-DD)'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Aggregate spam reports per phone number
        spam_stats = queryset.values('phone_number').annotate(
            spam_count=Count('id'),
            unique_reporters=Count('reported_by', distinct=True)
        ).order_by('-spam_count')
        
        # Convert to list for filtering
        spam_list = list(spam_stats)
        
        # Filter by minimum reports if specified
        min_reports = request.query_params.get('min_reports')
        if min_reports:
            try:
                min_reports = int(min_reports)
                spam_list = [s for s in spam_list if s['spam_count'] >= min_reports]
            except ValueError:
                return Response(
                    {'error': 'Invalid min_reports. Must be an integer.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Get detailed reporter info for each phone
        results = []
        for stat in spam_list:
            phone = stat['phone_number']
            
            # Get all reporters for this phone number
            phone_reports = queryset.filter(phone_number=phone)
            reporters = phone_reports.values_list('reported_by_id', flat=True).distinct()
            
            # Get most recent report
            latest_report = phone_reports.order_by('-created_at').first()
            
            results.append({
                'phone_number': phone,
                'spam_count': stat['spam_count'],
                'unique_reporters': stat['unique_reporters'],
                'reported_by_users': list(reporters),
                'latest_report_date': latest_report.created_at.isoformat() if latest_report else None,
                'latest_description': latest_report.description if latest_report else None
            })
        
        return Response(results)