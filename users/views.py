from django.utils.translation import gettext as _
from rest_framework import viewsets
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

from .models import User, KYCProfile
from .forms import CustomUserCreationForm, UserProfileForm
from .serializers import UserSerializer, KYCProfileSerializer

# --- API ViewSets ---

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class KYCProfileViewSet(viewsets.ModelViewSet):
    queryset = KYCProfile.objects.all()
    serializer_class = KYCProfileSerializer

# --- HTML Views ---

def login_view(request):
    if request.user.is_authenticated: return redirect('dashboard')
    if request.method == 'POST':
        phone = request.POST.get('phone_number') or request.POST.get('phone')
        password = request.POST.get('password')
        user = authenticate(request, phone_number=phone, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, _("Identifiants incorrects."))
    return render(request, 'login.html')

def register_view(request):
    if request.user.is_authenticated: return redirect('dashboard')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def dashboard_view(request):
    if request.user.role == 'TENANT': return redirect('management:tenant_dashboard')
    return redirect('management:landlord_dashboard')

def public_profile_view(request, user_id=None, slug=None):
    if slug: user = get_object_or_404(User, slug=slug)
    else: user = get_object_or_404(User, id=user_id)
    properties = user.properties.filter(is_published=True)
    stats = {
        'total_properties': properties.count(),
        'experience_years': user.years_of_experience or 0,
    }
    share_url = request.build_absolute_uri(reverse('public_profile_slug', kwargs={'slug': user.slug})) if user.slug else request.build_absolute_uri()
    return render(request, 'public_profile.html', {
        'viewed_user': user, 
        'properties': properties,
        'stats': stats,
        'share_url': share_url
    })

@login_required
def update_profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _("Profil mis à jour !"))
            return redirect('dashboard')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'profile_update.html', {'form': form})

def verify_phone_view(request):
    if request.user.is_authenticated:
        request.user.is_phone_verified = True
        request.user.save()
        return redirect('dashboard')
    return render(request, 'verify_phone.html')

def password_recovery_view(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        phone = request.GET.get('phone')
        user = User.objects.filter(phone_number=phone).first()
        if user:
            # Mask email if exists
            email_masked = ""
            if user.email:
                parts = user.email.split('@')
                email_masked = f"{parts[0][:2]}***@{parts[1]}"
            
            return JsonResponse({
                'exists': True,
                'has_email': bool(user.email),
                'email_masked': email_masked
            })
        return JsonResponse({'exists': False})

    if request.method == 'POST':
        phone = request.POST.get('phone')
        method = request.POST.get('method', 'whatsapp') # default to whatsapp for safety
        user = User.objects.filter(phone_number=phone).first()
        
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = reverse('password_reset_confirm_public', kwargs={'uidb64': uid, 'token': token})
            full_reset_url = request.build_absolute_uri(reset_url)
            
            if method == 'email' and user.email:
                from logertogo.emails import send_password_reset_email
                if send_password_reset_email(user, full_reset_url):
                    messages.success(request, _("Un lien de réinitialisation a été envoyé à votre adresse email."))
                else:
                    messages.error(request, _("Erreur lors de l'envoi de l'email. Veuillez utiliser WhatsApp."))
            else:
                # DigitalH standard: Show the link for WhatsApp copy-paste or just inform
                messages.info(request, _("Lien de réinitialisation prêt pour le support WhatsApp."))
                return render(request, 'recovery.html', {'reset_url': full_reset_url, 'show_wa_link': True})
        else:
            messages.error(request, _("Numéro inconnu."))
            
    return render(request, 'recovery.html')

def password_reset_confirm_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception: user = None
    
    if user and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password = request.POST.get('password')
            user.set_password(password)
            user.save()
            messages.success(request, _("Votre mot de passe a été mis à jour. Vous pouvez maintenant vous connecter."))
            return redirect('login')
            
        return render(request, 'password_reset_confirm_public.html', {'reset_user': user})
    messages.error(request, _("Lien invalide."))
    return redirect('password_recovery')

@login_required
def admin_generate_reset_link(request, user_id):
    if not request.user.is_staff:
        return JsonResponse({'error': _('Accès interdit')}, status=403)
    user = get_object_or_404(User, pk=user_id)
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    reset_url = request.build_absolute_uri(
        reverse('password_reset_confirm_public', kwargs={'uidb64': uid, 'token': token})
    )
    return JsonResponse({'reset_url': reset_url, 'phone': user.phone_number})
