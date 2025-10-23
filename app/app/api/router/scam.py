from django.urls import path
from app.api.viewsets.scam import CreateScamRecord

urlpatterns = [
    path('spam', CreateScamRecord.as_view(), name='scam-create'),
]