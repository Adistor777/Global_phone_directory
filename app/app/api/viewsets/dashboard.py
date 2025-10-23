from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from django.shortcuts import render
from app.models.interaction import Interaction
from app.models.scam import ScamRecord
from app.models.user import User
from django.db.models import Count, Q
from datetime import datetime, timedelta
import json


class DashboardView(APIView):
    """
    GET /api/dashboard
    Returns dashboard HTML or JSON data based on Accept header
    """
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request):
        user = request.user
        
        # Check if request wants HTML or JSON
        accept_header = request.META.get('HTTP_ACCEPT', '')
        
        if 'text/html' in accept_header or request.query_params.get('format') == 'html':
            # Return HTML dashboard
            context = self._get_dashboard_data(user)
            # Convert activity_trend to JSON string for JavaScript
            context['activity_trend'] = json.dumps(context['activity_trend'])
            return render(request, 'dashboard.html', context)
        else:
            # Return JSON data
            data = self._get_dashboard_data(user)
            return Response(data, status=200)
    
    def _get_dashboard_data(self, user):
        """Gather all dashboard statistics"""
        
        # Total interactions
        total_interactions = Interaction.objects.filter(
            Q(initiator=user) | Q(receiver=user)
        ).count()
        
        # Interactions by type
        interactions_by_type = Interaction.objects.filter(
            Q(initiator=user) | Q(receiver=user)
        ).values('interaction_type').annotate(count=Count('id'))
        
        interaction_stats = {
            'calls': 0,
            'messages': 0,
            'spam_reports': 0
        }
        
        for stat in interactions_by_type:
            if stat['interaction_type'] == 'call':
                interaction_stats['calls'] = stat['count']
            elif stat['interaction_type'] == 'message':
                interaction_stats['messages'] = stat['count']
            elif stat['interaction_type'] == 'spam_report':
                interaction_stats['spam_reports'] = stat['count']
        
        # Recent interactions (last 10)
        recent_interactions = Interaction.objects.filter(
            Q(initiator=user) | Q(receiver=user)
        ).select_related('initiator', 'receiver').order_by('-created_at')[:10]
        
        recent_list = []
        for interaction in recent_interactions:
            other_user = interaction.receiver if interaction.initiator == user else interaction.initiator
            recent_list.append({
                'type': interaction.interaction_type,
                'with': other_user.get_full_name() if other_user else interaction.receiver_phone,
                'date': interaction.created_at.strftime('%Y-%m-%d %H:%M'),
                'direction': 'outgoing' if interaction.initiator == user else 'incoming'
            })
        
        # Top contacts (most interacted)
        top_contacts_data = Interaction.objects.filter(
            initiator=user
        ).values('receiver_phone').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        top_contacts = []
        for contact in top_contacts_data:
            phone = contact['receiver_phone']
            receiver = User.objects.filter(phone_number=phone).first()
            top_contacts.append({
                'name': receiver.get_full_name() if receiver else phone,
                'phone': phone,
                'count': contact['count']
            })
        
        # Spam reports received (how many times this user was reported)
        spam_received = ScamRecord.objects.filter(
            phone_number=user.phone_number
        ).count()
        
        # Spam reports made by this user
        spam_reported = ScamRecord.objects.filter(
            reported_by=user
        ).count()
        
        # Activity trends (last 7 days)
        activity_trend = []
        for i in range(6, -1, -1):
            date = datetime.now() - timedelta(days=i)
            day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            count = Interaction.objects.filter(
                Q(initiator=user) | Q(receiver=user),
                created_at__gte=day_start,
                created_at__lt=day_end
            ).count()
            
            activity_trend.append({
                'date': date.strftime('%Y-%m-%d'),
                'day': date.strftime('%a'),
                'count': count
            })
        
        return {
            'user': {
                'name': user.get_full_name(),
                'phone': user.phone_number,
                'email': user.email or ''
            },
            'total_interactions': total_interactions,
            'interaction_stats': interaction_stats,
            'recent_interactions': recent_list,
            'top_contacts': top_contacts,
            'spam_stats': {
                'received': spam_received,
                'reported': spam_reported
            },
            'activity_trend': activity_trend
        }