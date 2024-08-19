from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, status, permissions
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.db.models import Q
from utils.permissions import IsBrowserAuthenticated


class RegisterUser(APIView):
    authentication_classes = [authentication.TokenAuthentication]

    def __error_invalid_field(self, field):
        return Response({
            field: "Cannot be empty"
        }, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        if not request.user.is_anonymous:
            return Response({
                "reason": "User already authenticated"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = request.data

        username: str = data.get("username")
        password: str = data.get("password")
        email: str = data.get("email")

        if not username:
            return self.__error_invalid_field("username")
        if not password:
            return self.__error_invalid_field("password")
        if not email:
            return self.__error_invalid_field("email")

        if User.objects.filter(
            Q(username=username) | Q(email=email)
        ).exists():
            return Response({
                "reason": "User already exists"
            }, status=status.HTTP_400_BAD_REQUEST)
            

        user = User.objects.create_user(username, email, password)
        return Response(status=status.HTTP_201_CREATED)
    

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
