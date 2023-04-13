from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.authtoken.views import Token
from rest_framework.decorators import action
from rest_framework import viewsets, status


from django.contrib import auth
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .permissions import UserProfilePermission
from api.serializers.user_serializers import UserSerializer, FriendshipSerializer
from api.serializers.education_serializers import EducationHistorySerializer
from api.models import Friendship, CustomUser, EducationHistory


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    permission_classes = [UserProfilePermission]
    serializer_class = UserSerializer
    lookup_field = "pk"

    filter_backends = []

    def get_user_info(self, request, user):
        token, created = Token.objects.get_or_create(user=user)
        abs_url = request.build_absolute_uri
        return {
            "username": user.full_name,
            "profile_picture": abs_url(user.profile_picture.url),
            "token": token.key,
            "url": abs_url(user.url),
        }

    def get_object(self):
        filter_kwargs = {self.lookup_field: self.kwargs[self.lookup_field]}
        return get_object_or_404(self.queryset, **filter_kwargs)

    def get_peoples_queryset(self, user):
        peoples = CustomUser.objects.exclude(id=user.id)
        if self.action == "level_mates":
            return peoples.filter(level=user.level)
        elif self.action == "school_mates":
            return peoples.filter(school=user.school)
        elif self.action == "friends":
            # Return the user's friends
            friend_requests = Friendship.objects.filter(
                Q(sender=user) | Q(receiver=user),
                status="accepted",
            )
            related_user_ids = list(*friend_requests.values_list("sender", "receiver"))
            return peoples.filter(id__in=related_user_ids)
        elif self.action == "suggested_friends":
            friend_requests = Friendship.objects.filter(
                Q(sender=user) | Q(receiver=user)
            )
            related_user_ids = list(*friend_requests.values_list("sender", "receiver"))
            return peoples.exclude(id__in=related_user_ids)

    def get_serializer_class(self):
        if self.action == "friend_request":
            return FriendshipSerializer
        elif self.action == "add_education":
            return EducationHistorySerializer
        return super().get_serializer_class()

    def get_queryset(self):
        if self.kwargs:
            user = self.get_object()
            if self.action.endswith(("mates", "friends")):
                return self.get_peoples_queryset(user)
            elif self.action == "add_education":
                return EducationHistory.objects.all()
            elif self.action == "friend_request":
                return Friendship.objects.filter(Q(sender=user) | Q(receiver=user))
        return super().get_queryset()

    @action(detail=True, methods=["post"])
    def add_education(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @action(detail=True)
    def friends(self, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get", "post", "put", "delete"])
    def friend_request(self, request, *args, **kwargs):
        user = request.user
        obj = self.get_object()
        queryset = self.get_queryset()  # Get user's friend_requests
        if user == obj:
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        try:
            friendship = queryset.get(Q(receiver=obj) | Q(sender=obj))
        except Friendship.DoesNotExist:
            if request.method == "POST":
                friendship = queryset.create(sender=user, receiver=obj)
            else:
                return Response("You are not friends")
        if request.method == "PUT":
            if friendship.receiver == user:
                friendship.status = "accepted"
                friendship.save()
        elif request.method == "DELETE":
            friendship.delete()
            return Response()
        serializer = self.get_serializer(friendship)
        return Response(serializer.data)

    @action(detail=True)
    def suggested_friends(self, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    @action(detail=True)
    def level_mates(self, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    @action(detail=True)
    def school_mates(self, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["put"])
    def change_password(self, request, *args, **kwargs):
        lizer = self.get_serializer(request.user, data=request.data)
        lizer.is_valid(raise_exception=True)
        lizer.save()
        auth.login(request, request.user)
        return Response({"detail": "Password changed"})

    @action(detail=True, methods=["get", "put"])
    def reset_password(self, request, *args, **kwargs):
        user = self.get_object()
        if request.method == "GET":
            code = user.reset_password()
            print(user.password_reset_code)
            # Send the code to users phone number
            return Response(
                {"detail": f"Reset code has been sent to '{user.phone_number}'"}
            )
        lizer = self.get_serializer(user, request.data)
        lizer.is_valid(raise_exception=True)
        auth.login(request, user)
        return Response(self.get_user_info(request, user))

    @action(detail=False, methods=["post"])
    def login(self, request, *args, **kwargs):
        lizer = self.get_serializer(data=request.data)
        lizer.is_valid(raise_exception=True)
        user = auth.authenticate(**lizer.data)
        auth.login(request, user)
        return Response(self.get_user_info(request, user))

    @action(detail=False, methods=["get"])
    def logout(self, request, *args, **kwargs):
        auth.logout(request)
        url = request.build_absolute_uri(reverse("api:users-login"))
        return Response(
            {"detail": "You have logout successfully", "login again": url},
            status=status.HTTP_410_GONE,
        )
