from django.shortcuts import render
from rest_framework.generics import RetrieveAPIView, RetrieveUpdateAPIView, UpdateAPIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FileUploadParser
from .serializers import UserFullInformationSerializer, UserInformationSerializer, UserPasswordSerializer, ProfilePictureSerializer
from .models import Profile


class IsBrowserAuthenticated(IsAuthenticated):
    """
    Does not check authentication on OPTIONS methods, used by browser to get CORS headers.

    https://github.com/encode/django-rest-framework/issues/5616
    """

    def has_permission(self, request, view):
        if request.method == 'OPTIONS':
            return True
        return request.user and request.user.is_authenticated


class UserFullInformationView(RetrieveUpdateAPIView):
    """
    Provides full information about a user, can only be accessed by the user itself.
    Used for introspection.
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsBrowserAuthenticated]
    serializer_class = UserFullInformationSerializer

    def get_object(self):
        return Profile.objects.get(user__id=self.request.user.id)


class PasswordUpdateView(UpdateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsBrowserAuthenticated]
    serializer_class = UserPasswordSerializer

    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():

            old_pwd = serializer.data.get("old_password")
            new_pwd = serializer.data.get("new_password")

            if not self.object.check_password(old_pwd):
                return Response({
                    "reason": "Wrong password"
                }, status=status.HTTP_400_BAD_REQUEST)

            self.object.set_password(new_pwd)
            self.object.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserInformationView(RetrieveAPIView):
    """
    Provides public information and username without authentication.
    """

    serializer_class = UserInformationSerializer

    def get_object(self):
        return Profile.objects.get(user__id=self.kwargs['userid'])
    

class ProfilePictureView(UpdateAPIView):
    serializer_class = ProfilePictureSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsBrowserAuthenticated]
    parser_classes = [MultiPartParser, FileUploadParser]

    #TODO: limit size

    def get_object(self):
        return self.request.user
