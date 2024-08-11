from django.shortcuts import render
from rest_framework.generics import RetrieveAPIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import UserFullInformationSerializer, UserInformationSerializer
from .models import Profile

class UserFullInformationView(RetrieveAPIView):
    """
    Provides full information about a user, can only be accessed by the user itself.
    Used for introspection.
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UserFullInformationSerializer

    def get_object(self):
        return Profile.objects.get(user__id=self.request.user.id)


class UserInformationView(RetrieveAPIView):
    """
    Provides public information and username without authentication.
    """

    serializer_class = UserInformationSerializer

    def get_object(self):
        return Profile.objects.get(user__id=self.kwargs['userid'])
    