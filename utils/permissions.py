from rest_framework.permissions import IsAuthenticated

class IsBrowserAuthenticated(IsAuthenticated):
    """
    Does not check authentication on OPTIONS methods, used by browser to get CORS headers.

    https://github.com/encode/django-rest-framework/issues/5616
    """

    def has_permission(self, request, view):
        if request.method == 'OPTIONS':
            return True
        return request.user and request.user.is_authenticated
