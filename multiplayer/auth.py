from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token

def get_user(token_key):
    try:
        token = Token.objects.get(key=token_key)
        return token.user
    except Token.DoesNotExist:
        return AnonymousUser()
