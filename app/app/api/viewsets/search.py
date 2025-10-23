from rest_framework.response import Response
from app.models.user import User
from app.models.contact import Contact
from django.db.models import Q, Value, IntegerField
from app.serializers import output
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.pagination import PageNumberPagination
from app.utils import calculate_name_similarity, get_phone_variants


def get_query_type(query):
    """Determine if query is phone number or name"""
    if not query:
        return None
    query = query.strip()
    if query and query[0].isdigit():
        return 'phone_number'
    return 'name'


class SearchView(APIView):
    """
    GET /api/search?q=<query>
    Search for users/contacts by name or phone number
    Supports fuzzy matching, pagination, and deduplication
    """
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)
    output_serializer_class = output.SearchOutputSerializer
    pagination_class = PageNumberPagination

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        
        if not query:
            return Response(
                {'error': 'Search query parameter "q" is required.'},
                status=400
            )
        
        search_type = get_query_type(query)
        results = []
        
        if search_type == 'phone_number':
            # Phone number search - exact match only
            results = self._search_by_phone(query)
        
        elif search_type == 'name':
            # Name search - fuzzy matching with ranking
            results = self._search_by_name(query)
        
        # Deduplicate by phone number (prefer User over Contact)
        results = self._deduplicate_results(results)
        
        # Paginate results
        paginator = self.pagination_class()
        paginated_results = paginator.paginate_queryset(results, request)
        
        output_serializer = self.output_serializer_class(paginated_results, many=True)
        return paginator.get_paginated_response(output_serializer.data)
    
    def _search_by_phone(self, query):
        """Search by phone number with variants"""
        from app.utils import normalize_phone_number
        
        try:
            # Try to normalize
            normalized = normalize_phone_number(query)
            variants = get_phone_variants(normalized)
        except:
            # If normalization fails, search with original
            variants = [query]
        
        # Search in Users first
        users = User.objects.filter(phone_number__in=variants)
        if users.exists():
            return list(users)
        
        # If no users found, search in Contacts
        contacts = Contact.objects.filter(phone_number__in=variants)
        return list(contacts)
    
    def _search_by_name(self, query):
        """Search by name with fuzzy matching and ranking"""
        query_lower = query.lower()
        
        # Search Users
        users_startswith = User.objects.filter(
            Q(first_name__istartswith=query) | Q(last_name__istartswith=query)
        ).distinct()
        
        users_contains = User.objects.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query)
        ).exclude(
            Q(first_name__istartswith=query) | Q(last_name__istartswith=query)
        ).distinct()
        
        # Search Contacts
        contacts_startswith = Contact.objects.filter(
            Q(first_name__istartswith=query) | Q(last_name__istartswith=query)
        ).distinct()
        
        contacts_contains = Contact.objects.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query)
        ).exclude(
            Q(first_name__istartswith=query) | Q(last_name__istartswith=query)
        ).distinct()
        
        # Combine results with ranking
        results = []
        
        # Priority 1: Users with name starting with query
        for user in users_startswith:
            user.match_score = calculate_name_similarity(query, user.get_full_name())
            results.append(user)
        
        # Priority 2: Contacts with name starting with query
        for contact in contacts_startswith:
            contact.match_score = calculate_name_similarity(query, contact.get_full_name())
            results.append(contact)
        
        # Priority 3: Users with name containing query
        for user in users_contains:
            user.match_score = calculate_name_similarity(query, user.get_full_name())
            results.append(user)
        
        # Priority 4: Contacts with name containing query
        for contact in contacts_contains:
            contact.match_score = calculate_name_similarity(query, contact.get_full_name())
            results.append(contact)
        
        # Sort by match score (highest first)
        results.sort(key=lambda x: getattr(x, 'match_score', 0), reverse=True)
        
        return results
    
    def _deduplicate_results(self, results):
        """Remove duplicates, preferring Users over Contacts"""
        seen_phones = set()
        deduplicated = []
        
        # First pass: Add all Users
        for item in results:
            if isinstance(item, User):
                if item.phone_number not in seen_phones:
                    seen_phones.add(item.phone_number)
                    deduplicated.append(item)
        
        # Second pass: Add Contacts not already in Users
        for item in results:
            if isinstance(item, Contact):
                if item.phone_number not in seen_phones:
                    seen_phones.add(item.phone_number)
                    deduplicated.append(item)
        
        return deduplicated


class SearchDetailsView(APIView):
    """
    GET /api/search/detail/<uuid:id>
    Get detailed information about a user or contact
    """
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)
    output_user_serializer_class = output.SearchDetailsUserOutputSerializer
    output_contact_serializer_class = output.SearchDetailsContactOutputSerializer

    def get(self, request, id):
        # Try to find as User first
        try:
            user = User.objects.get(id=id)
            output_serializer = self.output_user_serializer_class(
                user, 
                context={'request': request}
            )
            return Response(output_serializer.data, status=200)
        except User.DoesNotExist:
            pass
        
        # Try to find as Contact
        try:
            contact = Contact.objects.get(id=id)
            output_serializer = self.output_contact_serializer_class(contact)
            return Response(output_serializer.data, status=200)
        except Contact.DoesNotExist:
            return Response(
                {'error': 'Record not found.'},
                status=404
            )