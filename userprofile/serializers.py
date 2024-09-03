from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile

class UserPublicInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class UserFullInformationSerializer(serializers.ModelSerializer):
    """
    This class provides full user information. For user introspection.
    """
    email = serializers.CharField(source="user.email", required=False, allow_blank=False)
    username = serializers.CharField(source="user.username", required=False, allow_blank=False)
    first_name = serializers.CharField(source="user.first_name", required=False, allow_blank=True)
    last_name = serializers.CharField(source="user.last_name", required=False, allow_blank=True)
    picture = serializers.ImageField(required=False, allow_null=True, use_url=True, read_only=True)
    github = serializers.CharField(allow_blank=True)
    linkedin = serializers.CharField(allow_blank=True)
    is_publisher = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ("username", "email", "first_name", "last_name", "github", "linkedin", "picture", "is_publisher")

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
    
    def get_is_publisher(self, obj):
        return obj.user.groups.filter(name="Publishers").exists()


class UserPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    
    class Meta:
        model = User
    

#TODO: refactor User with Profile or Userprofile
class UserInformationSerializer(serializers.ModelSerializer):
    """
    This class provides user information except email.
    """
    username = serializers.CharField(source="user.username")
    picture = serializers.ImageField(allow_null=True, use_url=True)

    class Meta:
        model = Profile
        fields = ("username", "github", "linkedin", "picture")


class ProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("picture",)