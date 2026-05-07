from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from .models import Conversation, Message
from logersn.models import Property
from users.models import User

@login_required
def initiate_chat_view(request, property_id):
    """Commencer ou reprendre une conversation avec le propriétaire."""
    try:
        target_property = get_object_or_404(Property, id=property_id)
        
        # Statistique de clic
        target_property.clicks_count += 1
        target_property.save()
        
        owner = target_property.owner
        if owner == request.user:
            messages.info(request, _("C'est votre propre annonce !"))
            return redirect('messagerie')
            
        # Chercher une conversation existante liée à ce bien
        conversation = Conversation.objects.filter(
            topic=Conversation.TopicEnum.PROPERTY_INQUIRY,
            related_property=target_property,
            participants=request.user
        ).filter(participants=owner).order_by('-updated_at').first()
        
        # Si la conversation existe mais est expirée (> 10 jours d'inactivité), on en crée une nouvelle
        if conversation and conversation.is_expired:
            conversation = None

        if not conversation:
            conversation = Conversation.objects.create(
                topic=Conversation.TopicEnum.PROPERTY_INQUIRY,
                related_property=target_property,
                status=Conversation.StatusEnum.PENDING
            )
            conversation.participants.add(request.user, owner)
            
        return redirect(f"{reverse('messagerie')}?conv={conversation.id}")
    except Exception as e:
        messages.error(request, _("Erreur lors de l'initiation de la discussion. Veuillez réessayer."))
        return redirect('home')

@login_required
def initiate_pro_chat_view(request, user_id):
    """Initier une discussion directe avec un professionnel."""
    try:
        pro = get_object_or_404(User, id=user_id)
        if pro == request.user:
            messages.info(request, _("C'est vous-même !"))
            return redirect('messagerie')
            
        # Chercher une conversation GÉNÉRALE existante entre ces deux-là
        conversation = Conversation.objects.filter(
            topic=Conversation.TopicEnum.GENERAL,
            participants=request.user
        ).filter(participants=pro).order_by('-updated_at').first()
        
        if not conversation:
            conversation = Conversation.objects.create(
                topic=Conversation.TopicEnum.GENERAL,
                status=Conversation.StatusEnum.ACCEPTED
            )
            conversation.participants.add(request.user, pro)
            
        return redirect(f"{reverse('messagerie')}?conv={conversation.id}")
    except Exception:
        messages.error(request, _("Impossible de contacter ce professionnel."))
        return redirect('professionals_list')

@login_required
def update_chat_status_view(request, conversation_id, status):
    """Accepter ou refuser une discussion."""
    conv = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    if status in ['ACCEPTED', 'REJECTED']:
        conv.status = status
        conv.save()
    return redirect(f"{reverse('messagerie')}?conv={conv.id}")

@login_required
def send_message_view(request, conversation_id=None):
    if request.method == 'POST':
        content = request.POST.get('content', '')
        attachment = request.FILES.get('attachment')
        
        if not content and not attachment:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Message vide'}, status=400)
            return redirect('messagerie')
            
        conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
        
        if conversation.status == 'REJECTED':
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Conversation refusée'}, status=403)
            messages.error(request, "Cette conversation a été refusée.")
            return redirect('messagerie')
            
        if conversation.is_expired:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Cette discussion a expiré après 10 jours d\'inactivité.'}, status=403)
            messages.error(request, "Cette discussion a expiré après 10 jours d'inactivité. Veuillez relancer le contact depuis l'annonce.")
            return redirect('messagerie')
            
        msg = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=content,
            attachment=attachment
        )
        conversation.save() # Mettre à jour updated_at
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'id': msg.id,
                'content': msg.content,
                'sender': msg.sender.get_full_name(),
                'sender_id': msg.sender.id,
                'created_at': msg.created_at.strftime("%H:%M"),
                'attachment_url': msg.attachment.url if msg.attachment else None
            })
            
        return redirect(f"{reverse('messagerie')}?conv={conversation.id}")
    return redirect('messagerie')

@login_required
def sync_messages_view(request, conversation_id):
    """Endpoint pour le Polling AJAX (temps réel sans WebSocket)."""
    try:
        conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
        msgs = conversation.messages.all().order_by('created_at')
        
        data = []
        for msg in msgs:
            data.append({
                'id': msg.id,
                'content': msg.content,
                'sender_id': msg.sender.id,
                'sender': msg.sender.get_full_name() or msg.sender.email,
                'created_at': msg.created_at.strftime("%H:%M"),
                'attachment_url': msg.attachment.url if msg.attachment else None
            })
        return JsonResponse({'messages': data, 'status': conversation.status, 'is_expired': conversation.is_expired})
    except Exception:
        return JsonResponse({'error': 'Conversation inaccessible'}, status=403)

@login_required
def messagerie_view(request):
    """Vue principale de la messagerie style réseau social."""
    conversations = request.user.conversations.all().order_by('-updated_at')
    active_conv_id = request.GET.get('conv')
    active_conv = None
    if active_conv_id:
        active_conv = conversations.filter(id=active_conv_id).first()
    elif conversations.exists():
        active_conv = conversations.first()
        
    return render(request, 'chat/messagerie.html', {
        'conversations': conversations,
        'active_conv': active_conv
    })
