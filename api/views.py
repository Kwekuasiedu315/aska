from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.authtoken.views import Token
from rest_framework.decorators import action
from rest_framework import viewsets, status


from django.contrib import auth
from django.db.models import Q
from django.shortcuts import get_object_or_404
from . import serializers
from .permissions import UserProfilePermission, CurriculumPermission
from . import models
from .models import CustomUser, FriendRequest, School, Education, Lesson


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    permission_classes = [UserProfilePermission]
    serializer_class = serializers.UserSerializer
    lookup_field = "phone_number"

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
            return peoples.filter(school=user.school.name)
        elif self.action == "friends":
            # Return the user's friends
            friend_requests = FriendRequest.objects.filter(
                Q(sender=user) | Q(receiver=user),
                status="accepted",
            )
            related_user_ids = list(*friend_requests.values_list("sender", "receiver"))
            return peoples.filter(id__in=related_user_ids)
        elif self.action == "suggested_friends":
            friend_requests = FriendRequest.objects.filter(
                Q(sender=user) | Q(receiver=user)
            )
            related_user_ids = list(*friend_requests.values_list("sender", "receiver"))
            return peoples.exclude(id__in=related_user_ids)

    def get_serializer_class(self):
        if self.action == "friend_request":
            return serializers.FriendRequestSerializer
        elif self.action == "add_education":
            return serializers.EducationSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        if self.kwargs:
            user = self.get_object()
            if self.action.endswith(("mates", "friends")):
                return self.get_peoples_queryset(user)
            elif self.action == "add_education":
                return Education.objects.all()
            elif self.action == "friend_request":
                return FriendRequest.objects.filter(Q(sender=user) | Q(receiver=user))
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
            friend_request = queryset.get(Q(receiver=obj) | Q(sender=obj))
        except FriendRequest.DoesNotExist:
            if request.method == "POST":
                friend_request = queryset.create(sender=user, receiver=obj)
            else:
                return Response("You are not friends")
        if request.method == "PUT":
            if friend_request.receiver == user:
                friend_request.status = "accepted"
                friend_request.save()
            else:
                friend_request.delete()
        elif request.method == "DELETE":
            friend_request.delete()
        serializer = self.get_serializer(friend_request)
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
        url = request.build_absolute_uri(reverse("api:user-login"))
        return Response(
            {"detail": "You have logout successfully", "login again": url},
            status=status.HTTP_410_GONE,
        )


class SchoolProfileViewSet(viewsets.ModelViewSet):
    queryset = School.objects.all()
    serializer_class = serializers.SchoolSerializer


class CurriculumViewSet(viewsets.ModelViewSet):
    permission_classes = [CurriculumPermission]
    queryset = models.Curriculum.objects.all()
    lookup_field = "id"
    lookup_url_kwarg = "curriculum"

    def get_queryset(self):
        queryset = self.queryset
        curriculum = self.kwargs.get("curriculum", None)
        strand = self.kwargs.get("strand", None)
        substrand = self.kwargs.get("substrand", None)
        content_standard = self.kwargs.get("content_standard", None)
        learning_indicator = self.kwargs.get("learning_indicator", None)
        lesson = self.kwargs.get("lesson", None)
        if curriculum:
            queryset = get_object_or_404(queryset, id=curriculum).strand.all()
            if strand:
                queryset = get_object_or_404(queryset, number=strand).substrand.all()
                if substrand:
                    queryset = get_object_or_404(
                        queryset, number=substrand
                    ).content_standard.all()
                    if content_standard:
                        queryset = get_object_or_404(
                            queryset, number=content_standard
                        ).learning_indicator.all()
                        if learning_indicator:
                            queryset = get_object_or_404(
                                queryset, number=learning_indicator
                            ).lesson.all()
                            if lesson:
                                queryset = get_object_or_404(queryset, number=lesson)
        return queryset

    def get_serializer_class(self):
        if self.action == "strands":
            return serializers.StrandSerializer
        elif self.action == "substrands":
            return serializers.SubstrandSerializer
        elif self.action == "content_standards":
            return serializers.ContentStandardSerializer
        elif self.action == "learning_indicators":
            return serializers.LearningInidicatorSerializer
        elif self.action == "lessons":
            return serializers.LessonSerializer
        elif self.action == "questions":
            return serializers.QuestionSerializer
        return serializers.CurriculumSerializer

    @action(detail=False, url_path="(?P<curriculum>[^/.]+)")
    def strands(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        lizer = self.get_serializer(queryset, many=True)
        return Response(lizer.data)

    @action(detail=True, url_path="(?P<strand>\d+)")
    def substrands(self, *args, **kwargs):
        queryset = self.get_queryset()
        lizer = self.get_serializer(queryset, many=True)
        return Response(lizer.data)

    @action(
        detail=True,
        url_path="(?P<strand>\d+)/(?P<substrand>\d+)",
    )
    def content_standards(self, *args, **kwargs):
        queryset = self.get_queryset()
        lizer = self.get_serializer(queryset, many=True)
        return Response(lizer.data)

    @action(
        detail=True,
        url_path="(?P<strand>\d+)/(?P<substrand>\d+)/(?P<content_standard>\d+)",
    )
    def learning_indicators(self, *args, **kwargs):
        queryset = self.get_queryset()
        lizer = self.get_serializer(queryset, many=True)
        return Response(lizer.data)

    @action(
        detail=True,
        methods=["get", "post"],
        url_path="(?P<strand>\d+)/(?P<substrand>\d+)/(?P<content_standard>\d+)/questions",
    )
    def questions(self, request, *args, **kwargs):
        number = self.kwargs["content_standard"]
        substrand_number = self.kwargs["substrand"]
        lesson = models.ContentStandard.objects.get(
            number=number, substrand__number=substrand_number
        )
        queryset = lesson.questions.all()
        lizer = self.get_serializer(queryset, many=True)
        if request.method == "POST":
            lizer = self.get_serializer(data=request.data)
            lizer.is_valid(raise_exception=True)
            lizer.validated_data["lesson"] = lesson
            lizer.save()
        return Response(lizer.data)

    @action(
        detail=True,
        url_path="(?P<strand>\d+)/(?P<substrand>\d+)/(?P<content_standard>\d+)/(?P<learning_indicator>\d+)",
    )
    def lessons(self, *args, **kwargs):
        queryset = self.get_queryset()
        lizer = self.get_serializer(queryset, many=True)
        return Response(lizer.data)


class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.QuestionSerializer
    queryset = models.Question.objects.all()

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ["multiple_choices", "multiple_choices_detail"]:
            queryset = queryset.filter(question_type="mc")
        return queryset

    def get_serializer_class(self, *args, **kwargs):
        if self.action in ["multiple_choices", "multiple_choices_detail"]:
            return serializers.MCAQuestionSerializer
        return super().get_serializer_class(*args, **kwargs)

    @action(detail=False, methods=["get", "post"])
    def multiple_choices(self, *args, **kwargs):
        queryset = self.get_queryset()
        lizer = self.get_serializer(queryset, many=True)
        return Response(lizer.data)

    @action(
        detail=False, methods=["get", "put"], url_path="multiple_choices/(?P<pk>\d+)"
    )
    def multiple_choices_detail(self, request, *args, **kwargs):
        obj = self.get_object()
        lizer = self.get_serializer(obj)
        if request.method == "PUT":
            lizer = self.get_serializer(data=request.data)
            lizer.is_valid(raise_exception=True)
            answer = request.data.get("answer", None)
        return Response(lizer.data)
