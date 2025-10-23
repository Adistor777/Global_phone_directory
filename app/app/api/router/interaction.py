from django.urls import path
from app.api.viewsets.interaction import (
    InteractionView,
    RecentInteractionsView,
    TopContactsView,
    SpamStatsView
)

urlpatterns = [
    path('interaction', InteractionView.as_view(), name='interaction'),
    path('interactions/recent', RecentInteractionsView.as_view(), name='interactions-recent'),
    path('interactions/top', TopContactsView.as_view(), name='interactions-top'),
    path('interactions/spam-stats', SpamStatsView.as_view(), name='interactions-spam-stats'),
]