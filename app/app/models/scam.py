from app.mixins import TimeStampModelMixin
from django.db import models
import uuid


class ScamRecord(TimeStampModelMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=20, db_index=True)
    reported_by = models.ForeignKey('User', on_delete=models.SET_NULL, related_name='scam_reports', null=True)
    description = models.CharField(max_length=500, blank=True, default='')
    created_by = models.ForeignKey('User', on_delete=models.SET_NULL, related_name='created_scam_records', null=True)
    updated_by = models.ForeignKey('User', on_delete=models.SET_NULL, related_name='updated_scam_records', null=True)

    def save(self, *args, **kwargs):
        if self.phone_number:
            try:
                from app.utils import normalize_phone_number
                self.phone_number = normalize_phone_number(self.phone_number)
            except:
                pass
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Spam: {self.phone_number}"

    class Meta:
        db_table = 'scam_records'
        verbose_name = 'Spam Report'
        verbose_name_plural = 'Spam Reports'
        constraints = [
            models.UniqueConstraint(
                fields=["reported_by", "phone_number"],
                name="unique_phone_number_reported_by",
            ),
        ]