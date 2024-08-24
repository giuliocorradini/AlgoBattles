from rest_framework import serializers
from userprofile.models import Profile

class UserLobbySerializer(serializers.ModelSerializer):
    """
    This class provides user information except email.
    """
    username = serializers.CharField(source="user.username")
    id = serializers.IntegerField(source="user.id")
    picture = serializers.ImageField(allow_null=True, use_url=True)

    class Meta:
        model = Profile
        fields = ("id", "username", "picture")