from rest_framework import permissions

class IsPublisherPermission(permissions.BasePermission):
    """
    Custom permission to only allow users in the 'Publishers' group.
    """

    def has_permission(self, request, view):
        if not request.user:
            return False
        
        return request.user.groups.filter(name='Publishers').exists()