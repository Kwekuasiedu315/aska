from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS


class UserProfilePermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if view.action in ["update", "partial_update", "destroy", "add_education"]:
            return user == view.get_object()
        elif view.action == "friend_request":
            if user.is_authenticated:
                friendship = user.friendship_status(view.get_object())
                if request.method == "POST":
                    return (user != view.get_object()) and not bool(friendship)
                elif request.method == "PUT":
                    if not bool(friendship):
                        return False
                    elif user == view.get_object():
                        return False
                    return True
                elif request.method == "DELETE":
                    return bool(friendship)
                return True
            return False
        elif view.action in ["create"]:
            return not user.is_authenticated
        elif view.action in ["change_password"]:
            return user.is_authenticated
        return True
