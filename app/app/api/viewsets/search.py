from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q, Count
from fuzzywuzzy import fuzz

from app.models import User, Contact, ScamRecord
from app.serializers.output.user import UserOutputSerializer
from app.serializers.output.contact import ContactOutputSerializer
from app.utils import normalize_phone_number


class SearchView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        query = request.query_params.get('q', '').strip()
        
        if not query:
            return Response(
                {'error': 'Search query is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Determine if searching by phone or name
        is_phone_search = query.replace('+', '').replace(' ', '').replace('-', '').isdigit()
        
        results = []
        
        if is_phone_search:
            # Phone number search (exact match)
            try:
                normalized_phone = normalize_phone_number(query)
                
                # Search users
                users = User.objects.filter(phone_number=normalized_phone)
                for user in users:
                    spam_count = ScamRecord.objects.filter(phone_number=normalized_phone).count()
                    results.append({
                        'id': str(user.id),
                        'name': user.get_full_name(),
                        'phone_number': user.phone_number,
                        'is_registered': True,
                        'spam_likelihood': spam_count,
                        'match_score': 100
                    })
                
                # Search contacts if no user found
                if not users:
                    contacts = Contact.objects.filter(phone_number=normalized_phone)
                    for contact in contacts:
                        spam_count = ScamRecord.objects.filter(phone_number=normalized_phone).count()
                        results.append({
                            'id': str(contact.id),
                            'name': f"{contact.first_name} {contact.last_name}".strip(),
                            'phone_number': contact.phone_number,
                            'is_registered': False,
                            'spam_likelihood': spam_count,
                            'match_score': 100
                        })
            
            except Exception as e:
                return Response(
                    {'error': f'Invalid phone number: {str(e)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        else:
            # Name search (fuzzy match)
            # Search users
            users = User.objects.filter(
                Q(first_name__icontains=query) | Q(last_name__icontains=query)
            )
            
            for user in users:
                name = user.get_full_name()
                match_score = fuzz.ratio(query.lower(), name.lower())
                spam_count = ScamRecord.objects.filter(phone_number=user.phone_number).count()
                
                results.append({
                    'id': str(user.id),
                    'name': name,
                    'phone_number': user.phone_number,
                    'is_registered': True,
                    'spam_likelihood': spam_count,
                    'match_score': match_score,
                    'type': 'user'
                })
            
            # Search contacts
            contacts = Contact.objects.filter(
                Q(first_name__icontains=query) | Q(last_name__icontains=query)
            )
            
            for contact in contacts:
                name = f"{contact.first_name} {contact.last_name}".strip()
                match_score = fuzz.ratio(query.lower(), name.lower())
                spam_count = ScamRecord.objects.filter(phone_number=contact.phone_number).count()
                
                results.append({
                    'id': str(contact.id),
                    'name': name,
                    'phone_number': contact.phone_number,
                    'is_registered': False,
                    'spam_likelihood': spam_count,
                    'match_score': match_score,
                    'type': 'contact'
                })
            
            # Sort by match score
            results.sort(key=lambda x: x['match_score'], reverse=True)
            
            # Deduplicate - prioritize users over contacts
            seen_phones = set()
            deduplicated = []
            
            for result in results:
                phone = result['phone_number']
                if phone not in seen_phones:
                    seen_phones.add(phone)
                    deduplicated.append(result)
            
            results = deduplicated
        
        # Limit to 10 results
        results = results[:10]
        
        return Response({
            'results': results,
            'count': len(results)
        })


class SearchDetailsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id):
        """Get detailed information about a search result"""
        
        # Try to find as user first
        try:
            user = User.objects.get(id=id)
            spam_count = ScamRecord.objects.filter(phone_number=user.phone_number).count()
            
            # Check if requester has this user in contacts
            has_in_contacts = Contact.objects.filter(
                created_by=request.user,
                phone_number=user.phone_number
            ).exists()
            
            return Response({
                'id': str(user.id),
                'name': user.get_full_name(),
                'phone_number': user.phone_number,
                'email': user.email if has_in_contacts else None,  # Privacy: only show email if in contacts
                'is_registered': True,
                'spam_likelihood': spam_count,
            })
        
        except User.DoesNotExist:
            pass
        
        # Try to find as contact
        try:
            contact = Contact.objects.get(id=id)
            spam_count = ScamRecord.objects.filter(phone_number=contact.phone_number).count()
            
            return Response({
                'id': str(contact.id),
                'name': f"{contact.first_name} {contact.last_name}".strip(),
                'phone_number': contact.phone_number,
                'email': None,
                'is_registered': False,
                'spam_likelihood': spam_count,
            })
        
        except Contact.DoesNotExist:
            return Response(
                {'error': 'Record not found'},
                status=status.HTTP_404_NOT_FOUND
            )