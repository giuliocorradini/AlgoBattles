from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile

class UserFullInformationSerializer(serializers.ModelSerializer):
    """
    This class provides full user information. For user introspection.
    """
    email = serializers.CharField(source="user.email")
    username = serializers.CharField(source="user.username")
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")

    class Meta:
        model = Profile
        fields = ("username", "email", "first_name", "last_name", "github", "linkedin", "picture")


class UserPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    
    class Meta:
        model = User
    

class UserInformationSerializer(serializers.ModelSerializer):
    """
    This class provides user information except email.
    """
    username = serializers.CharField(source="user.username")

    class Meta:
        model = Profile
        fields = ("username", "github", "linkedin", "picture")


