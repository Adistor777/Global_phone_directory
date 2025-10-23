from app.mixins import TimeStampModelMixin
from django.db import models
import uuid


class Contact(TimeStampModelMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, blank=True)
    phone_number = models.CharField(max_length=20, db_index=True)  # Changed from 10 to 20
    created_by = models.ForeignKey('User', on_delete=models.CASCADE, related_name='created_contacts')
    updated_by = models.ForeignKey('User', on_delete=models.SET_NULL, related_name='updated_contacts', null=True)

    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()
    
    def save(self, *args, **kwargs):
        # Normalize phone number before saving
        if self.phone_number:
            try:
                from app.utils import normalize_phone_number
                self.phone_number = normalize_phone_number(self.phone_number)
            except:
                pass  # Keep original if normalization fails
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.get_full_name()} - {self.phone_number}"

    class Meta:
        db_table = 'contacts'
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'
        constraints = [
            models.UniqueConstraint(
                fields=["phone_number", "created_by"],
                name="unique_phone_number_created_by",
            ),
        ]