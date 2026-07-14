from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from management.models import Notification

@login_required
def get_unread_notifications(request):
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:10]
    data = [
        {
            'id': str(n.id),
            'title': n.title,
            'message': n.message,
            'link': n.link,
            'time': n.created_at.strftime('%d/%m/%Y %H:%M')
        }
        for n in notifications
    ]
    return JsonResponse({'status': 'success', 'count': notifications.count(), 'notifications': data})

@login_required
def mark_notifications_read(request):
    if request.method == 'POST':
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)
