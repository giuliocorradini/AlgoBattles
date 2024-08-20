from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import authentication, status, permissions
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.db.models import Q
from utils.permissions import IsBrowserAuthenticated
from .serializers import UserSerializer
from rest_framework.permissions import BasePermission


class IsUnauthenticated(BasePermission):
    """
    Allows access to unauthenticated users only. Always consent access to OPTIONS
    """

    def has_permission(self, request, view):
        if request.method == "OPTIONS":
            return True
        
        return not request.user.is_authenticated


class RegisterUser(CreateAPIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = (IsUnauthenticated,)
    serializer_class = UserSerializer
    queryset = User.objects.all()
    

class Logout(APIView):
    """Destroys a valid token"""

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        request.auth.delete()
        logout(request)
        return Response(status=status.HTTP_205_RESET_CONTENT)
    

class ValidateTokenView(APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (IsBrowserAuthenticated,)

    def post(self, request):
        """Returns 204 if the authorization token is valid. Else 401 unauthorized"""

        return Response(status.HTTP_204_NO_CONTENT)
