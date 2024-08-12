from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile

class UserFullInformationSerializer(serializers.ModelSerializer):
    """
    This class provides full user information. For user introspection.
    """
    email = serializers.CharField(source="user.email", required=False)
    username = serializers.CharField(source="user.username", required=False)
    first_name = serializers.CharField(source="user.first_name", required=False)
    last_name = serializers.CharField(source="user.last_name", required=False)
    picture = serializers.ImageField(required=False, allow_null=True, use_url=True)

    class Meta:
        model = Profile
        fields = ("username", "email", "first_name", "last_name", "github", "linkedin", "picture")

    class UserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ['username', 'email', 'first_name', 'last_name']

    def update(self, instance, validated_data):
        user_data = validated_data.get("user")

        if user_data:
            validated_data.pop("user")

            user_serializer = self.UserSerializer(instance.user, data=user_data, partial=True)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

        return super().update(instance, validated_data)


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
    picture = serializers.ImageField(allow_null=True, use_url=True)

    class Meta:
        model = Profile
        fields = ("username", "github", "linkedin", "picture")


