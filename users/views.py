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
        phone = request.POST.get('full_phone') or request.POST.get('phone_number') or request.POST.get('phone')
        password = request.POST.get('password')
        user = authenticate(request, phone_number=phone, password=password)
        if user:
            login(request, user, backend='users.backends.PhoneOrEmailBackend')
            return redirect('dashboard')
        messages.error(request, _("Identifiants incorrects."))
    return render(request, 'login.html')

def register_view(request):
    if request.user.is_authenticated: return redirect('dashboard')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='users.backends.PhoneOrEmailBackend')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def dashboard_view(request):
    """Redirection intelligente selon le rôle de l'utilisateur."""
    user = request.user
    if user.role == User.RoleEnum.TENANT:
        return redirect('management:tenant_dashboard')
    elif user.role in [User.RoleEnum.LANDLORD, User.RoleEnum.AGENCY, User.RoleEnum.BROKER, User.RoleEnum.AGENT]:
        return redirect('management:landlord_dashboard')
    elif user.is_staff:
        return redirect('admin:index')
    return redirect('home')

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
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.headers.get('x-requested-with') == 'XMLHttpRequest'
    if is_ajax:
        email = request.GET.get('email')
        phone = request.GET.get('phone')
        if email:
            user = User.objects.filter(email=email).first()
            return JsonResponse({'exists': user is not None})
        elif phone:
            user = User.objects.filter(phone_number=phone).first()
            return JsonResponse({'exists': user is not None})
        return JsonResponse({'exists': False})

    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = reverse('password_reset_confirm_public', kwargs={'uidb64': uid, 'token': token})
            full_reset_url = request.build_absolute_uri(reset_url)
            
            from logertogo.emails import send_password_reset_email
            if send_password_reset_email(user, full_reset_url):
                messages.success(request, _("Un lien de réinitialisation a été envoyé à votre adresse email."))
                return render(request, 'recovery.html', {'success': True})
            else:
                messages.error(request, _("Erreur lors de l'envoi de l'email. Veuillez contacter le support."))
        else:
            messages.error(request, _("Adresse email inconnue."))
            
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
