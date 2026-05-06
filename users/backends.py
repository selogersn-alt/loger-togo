from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

class PhoneOrEmailBackend(ModelBackend):
    """
    Authentification personnalisée permettant de se connecter soit avec le numéro de téléphone,
    soit avec l'adresse email.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
            
        try:
            # On cherche l'utilisateur par téléphone OU par email
            user = UserModel.objects.get(Q(phone_number=username) | Q(email=username))
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            return None
        except UserModel.MultipleObjectsReturned:
            # En cas théorique de doublon (ne devrait pas arriver avec les contraintes Unique)
            return UserModel.objects.filter(Q(phone_number=username) | Q(email=username)).first()
        return None
