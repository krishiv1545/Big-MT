from django.db import models
import uuid

from core_APP.mixins.models import UserTrackingMixin, TimestampMixin


class ChatRoom(TimestampMixin, UserTrackingMixin, models.Model):
    
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    pin = models.CharField(max_length=4)

    def __str__(self):
        return f"ChatRoom ({self.uuid})"
