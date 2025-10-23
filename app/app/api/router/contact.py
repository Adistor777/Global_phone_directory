from django.urls import path
from app.api.viewsets.contact import ContactView

urlpatterns = [
    path('contact', ContactView.as_view(), name='contact'),
]