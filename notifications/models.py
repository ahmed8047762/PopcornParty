from django.db import models
from django.conf import settings
from events.models import Event

# Create your models here.

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('join_request', 'Join Request'),
        ('invitation', 'Invitation'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='notifications_received'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications_sent',
        null=True,
        blank=True
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        default='invitation'
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.notification_type} notification for {self.user.email}: {self.message}'
