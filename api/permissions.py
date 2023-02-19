from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS


class UserProfilePermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if view.action in ["update", "partial_update", "destroy", "add_education"]:
            return user == view.get_object()
        elif view.action == "friend_request":
            if user.is_authenticated:
                status = user.friend_request_status(view.get_object())
                if request.method == "POST":
                    return not bool(status)
                elif request.method == "PUT":
                    return bool(status)
                return True
            return False
        elif view.action in ["create"]:
            return not user.is_authenticated
        elif view.action in ["change_password"]:
            return user.is_authenticated
        return True


class CurriculumPermission(BasePermission):
    def has_permission(self, request, view):
        return True
