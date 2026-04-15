from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import UserMeSerializer

class UserMeView(APIView):
    """
    Renvoie les informations de l'utilisateur actuellement connecté via JWT.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserMeSerializer(request.user)
        return Response(serializer.data)
