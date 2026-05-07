import uuid
from django.db import models
from django.conf import settings
from logersn.models import Property

User = settings.AUTH_USER_MODEL

class Conversation(models.Model):
    class TopicEnum(models.TextChoices):
        GENERAL = 'GENERAL', 'Général'
        PROPERTY_INQUIRY = 'PROPERTY_INQUIRY', 'Demande Information Bien'
        INCIDENT_CLAIM = 'INCIDENT_CLAIM', 'Réclamation/Incident'
        SUPPORT = 'SUPPORT', 'Support Technique'

    class StatusEnum(models.TextChoices):
        PENDING = 'PENDING', 'En attente'
        ACCEPTED = 'ACCEPTED', 'Acceptée'
        REJECTED = 'REJECTED', 'Refusée'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participants = models.ManyToManyField(User, related_name='conversations')
    topic = models.CharField(max_length=50, choices=TopicEnum.choices, default=TopicEnum.GENERAL)
    status = models.CharField(max_length=20, choices=StatusEnum.choices, default=StatusEnum.PENDING)
    
    # Liens optionnels
    related_property = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Conversation {self.id} - {self.get_topic_display()}"

    @property
    def is_expired(self):
        """Une discussion expire après 10 jours d'inactivité."""
        from django.utils import timezone
        import datetime
        return timezone.now() > self.updated_at + datetime.timedelta(days=10)


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    attachment = models.ImageField(upload_to='chat_images/', null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message de {self.sender.email} à {self.created_at.strftime('%Y-%m-%d %H:%M')}"
