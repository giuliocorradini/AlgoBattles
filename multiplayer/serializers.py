from rest_framework import serializers
from userprofile.models import Profile
from .models import Challenge

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


class ChallengeSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()

    class Meta:
        model = Challenge
        fields = ("id", "sender")

    def get_sender(self, obj: Challenge):
        user = Profile.objects.filter(user=obj.starter.user).get()
        return UserLobbySerializer(user).data
