from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .models import Conversation, Message
from logersn.models import Property
from users.models import User

@login_required
def initiate_chat_view(request, property_id):
    """Commencer ou reprendre une conversation avec le propriétaire."""
    target_property = get_object_or_404(Property, id=property_id)
    target_property.clicks_count += 1
    target_property.save()
    
    owner = target_property.owner
    if owner == request.user:
        messages.info(request, "C'est votre propre annonce !")
        return redirect('dashboard')
        
    conversation = Conversation.objects.filter(
        topic=Conversation.TopicEnum.PROPERTY_INQUIRY,
        related_property=target_property,
        participants=request.user
    ).filter(participants=owner).first()
    
    if not conversation:
        conversation = Conversation.objects.create(
            topic=Conversation.TopicEnum.PROPERTY_INQUIRY,
            related_property=target_property
        )
        conversation.participants.add(request.user, owner)
        
    return redirect(f"{reverse('dashboard')}?conv={conversation.id}")

@login_required
def send_message_view(request, conversation_id=None):
    if request.method == 'POST':
        content = request.POST.get('content')
        if not content:
            return redirect('dashboard')
            
        conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
        Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=content
        )
        conversation.save() # Pour mettre à jour updated_at
        
        return redirect(f"{reverse('dashboard')}?conv={conversation.id}")
    return redirect('dashboard')
