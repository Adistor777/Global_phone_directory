from django.urls import path
from app.api.viewsets.dashboard import DashboardView

urlpatterns = [
    path('dashboard', DashboardView.as_view(), name='dashboard'),
]