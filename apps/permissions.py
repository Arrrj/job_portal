from rest_framework.permissions import BasePermission


class IsEmployer(BasePermission):
    message = None

    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.roles == 'employer':
            return True
        self.message = "You must be an employer to access this resource."
        return False


class IsCandidate(BasePermission):
    message = None

    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.roles == 'candidate':
            return True
        self.message = "You must be an candidate to access this resource."
        return False


class IsStaff(BasePermission):
    message = None

    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.is_staff:
            return True
        self.message = "You must be an admin to access this resource."
        return False