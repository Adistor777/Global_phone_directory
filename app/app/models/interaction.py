from app.mixins import TimeStampModelMixin
from django.db import models
import uuid


class Interaction(TimeStampModelMixin):
    """
    Model to track user interactions (calls, messages, spam reports)
    Part 2: User Interaction Dashboard
    """
    
    INTERACTION_TYPES = [
        ('call', 'Call'),
        ('message', 'Message'),
        ('spam_report', 'Spam Report'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    initiator = models.ForeignKey(
        'User', 
        on_delete=models.CASCADE, 
        related_name='initiated_interactions',
        help_text="User who started the interaction"
    )
    receiver = models.ForeignKey(
        'User', 
        on_delete=models.CASCADE, 
        related_name='received_interactions',
        null=True,
        blank=True,
        help_text="User who received the interaction"
    )
    receiver_phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Phone number if receiver is not a registered user"
    )
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES, db_index=True)
    
    # JSON field for metadata (call duration, message content, etc.)
    metadata = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        receiver_info = self.receiver.phone_number if self.receiver else self.receiver_phone
        return f"{self.initiator.phone_number} -> {receiver_info} ({self.interaction_type})"
    
    class Meta:
        db_table = 'interactions'
        verbose_name = 'Interaction'
        verbose_name_plural = 'Interactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['initiator', 'interaction_type']),
            models.Index(fields=['receiver', 'interaction_type']),
            models.Index(fields=['created_at']),
        ]