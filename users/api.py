from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import SolvencyDocument, User
from .serializers import UserMeSerializer, SolvencyDocumentSerializer, UserSerializer

class RegisterView(APIView):
    """
    API for native user registration.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        email = data.get('email')
        phone = data.get('phone_number')
        password = data.get('password')
        role = data.get('role', User.RoleEnum.TENANT)
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        company_name = data.get('company_name', '')

        if not phone or not password:
            return Response({'error': 'Numéro de téléphone et mot de passe requis.'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(phone_number=phone).exists():
            return Response({'error': 'Ce numéro de téléphone est déjà utilisé.'}, status=status.HTTP_400_BAD_REQUEST)

        if email and User.objects.filter(email=email).exists():
            return Response({'error': 'Cet email est déjà utilisé.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.create_user(
                phone_number=phone,
                email=email,
                password=password,
                role=role,
                first_name=first_name,
                last_name=last_name,
                company_name=company_name
            )
            return Response({'message': 'Compte créé avec succès.'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserMeView(APIView):
    """
    Renvoie les informations de l'utilisateur actuellement connecté via JWT.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserMeSerializer(request.user)
        return Response(serializer.data)

class SolvencyDocumentViewSet(viewsets.ModelViewSet):
    serializer_class = SolvencyDocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.solvency_docs.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
