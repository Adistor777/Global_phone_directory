from django.urls import path
from app.api.viewsets.search import SearchView, SearchDetailsView

urlpatterns = [
    path('search', SearchView.as_view(), name='user-search'),
    path('search/detail/<uuid:id>', SearchDetailsView.as_view(), name='user-search-details'),
]