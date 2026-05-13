from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

class PhoneOrEmailBackend(ModelBackend):
    """
    Authentification personnalisée permettant de se connecter soit avec le numéro de téléphone,
    soit avec l'adresse email. Gère également la rétrocompatibilité des anciens numéros sans code pays.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
            
        if not username:
            return None
            
        # Création des variations possibles du nom d'utilisateur (pour la rétrocompatibilité)
        possible_usernames = [username]
        
        # Si le username commence par +228, on essaie aussi sans le +228
        if username.startswith('+228'):
            possible_usernames.append(username[4:])
        # Si le username commence par 00228, on essaie aussi sans
        elif username.startswith('00228'):
            possible_usernames.append(username[5:])
            
        try:
            # On cherche l'utilisateur par téléphone (toutes variations) OU par email
            user = UserModel.objects.filter(
                Q(phone_number__in=possible_usernames) | Q(email=username)
            ).first()
            
            if user and user.check_password(password):
                return user
        except Exception:
            return None
            
        return None
