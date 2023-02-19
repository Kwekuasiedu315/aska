from rest_framework import serializers
from rest_framework.authtoken.models import Token

from django.contrib.auth import authenticate
from django.db.models import Q

from . import models
from . import choices
from .models import CustomUser, FriendRequest, Telephone
from .fields import user_serializer_fields


class UserSerializer(serializers.ModelSerializer):
    gender = serializers.ChoiceField(choices=choices.GENDER, allow_blank=True)
    school = serializers.SerializerMethodField("get_school")
    educations = serializers.SerializerMethodField("get_educations")
    level = serializers.ChoiceField(choices=choices.LEVEL, allow_blank=True)
    friend_request_status = serializers.SerializerMethodField()
    url = serializers.HyperlinkedIdentityField(
        view_name="api:user-detail", lookup_field="phone_number"
    )

    @property
    def user(self):
        return self.context["request"].user

    @property
    def action(self):
        return self.context["view"].action

    @property
    def request(self):
        return self.context["request"]

    def get_friend_request_status(self, instance):
        user = self.user
        return user.friend_request_status(instance)

    def get_school(self, instance):
        if instance.current_school:
            return instance.current_school.name

    def get_educations(self, instance):
        if instance.educations:
            return [edu.school.name for edu in instance.educations]

    def validate(self, attrs):
        if self.action == "login":
            phone_number = attrs["phone_number"]
            password = attrs["password"]
            user = authenticate(phone_number=phone_number, password=password)
            if not user:
                raise serializers.ValidationError(
                    {"login_error": "Phone number and password doesn't match"}
                )
        return attrs

    def validate_new_password(self, value):
        if len(value) < 5:
            raise serializers.ValidationError("Password is too short")
        return value

    def validate_old_password(self, value):
        if not self.user.check_password(value):
            raise serializers.ValidationError("Incorrect password")
        return value

    def validate_code(self, value):
        if value != self.instance.password_reset_code:
            raise serializers.ValidationError("Invalid Code")
        return value

    def get_fields(self):
        fields = super().get_fields()
        if self.action == "change_password":
            return {
                "old_password": serializers.CharField(write_only=True),
                "new_password": serializers.CharField(write_only=True),
            }
        elif self.action == "login":
            return {
                "phone_number": serializers.CharField(),
                "password": serializers.CharField(),
            }
        elif self.action == "reset_password":
            return {
                "code": serializers.CharField(write_only=True),
                "new_password": serializers.CharField(write_only=True),
            }
        elif self.action == "create":
            fields.pop("is_active")
        elif self.action == "profile":
            fields.pop("password")
        return fields

    def to_representation(self, instance):
        if self.action in ("update", "login", "retrieve"):
            return super().to_representation(instance)
        abs_url = self.context["request"].build_absolute_uri
        data = {
            "username": instance.full_name,
            "profile_picture": abs_url(instance.profile_picture.url),
            "url": abs_url(instance.url),
        }
        if self.action == "create":
            token = Token.objects.create(user=instance)
            data["token"] = token.key
        return data

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user

    def update(self, instance, validated_data):
        if self.action in ["change_password", "confirm_reset_code"]:
            instance.set_password(validated_data["new_password"])
            instance.save()
        return super().update(instance, validated_data)

    class Meta:
        fields = user_serializer_fields
        model = CustomUser
        extra_kwargs = {
            "password": {"write_only": True},
            "points": {"read_only": True},
            "last_login": {"read_only": True},
            "date_joined": {"read_only": True},
        }


class FriendRequestSerializer(serializers.ModelSerializer):
    def get_user(self, friendship):
        user = self.context["request"].user
        if friendship.sender != user:
            return friendship.sender
        return friendship.receiver

    def to_representation(self, instance):
        user = self.get_user(friendship=instance)
        absolute_url = self.context["request"].build_absolute_uri
        return {
            "username": user.full_name,
            "sender": user == instance.receiver,
            "status": instance.status,
            "time": instance.timestamp,
            "url": absolute_url(user.url),
            "request_url": absolute_url(user.url) + "friend_request/",
        }

    class Meta:
        model = FriendRequest
        fields = []


class SchoolSerializer(serializers.ModelSerializer):
    owner = serializers.ChoiceField(choices=choices.SCHOOL_OWNER)
    url = serializers.HyperlinkedIdentityField(
        view_name="api:school-detail", lookup_field="pk"
    )

    def create(self, validated_data):
        validated_data["added_by"] = self.context["request"].user
        return super().create(validated_data)

    class Meta:
        model = models.School
        exclude = ["added_by", "visible"]


class EducationSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

    class Meta:
        model = models.Education
        fields = ["school", "date_started", "date_completed"]


class CurriculumSerializer(serializers.ModelSerializer):
    strands = serializers.SerializerMethodField()

    def get_strands(self, instance):
        abs_url = self.context["request"].build_absolute_uri
        return abs_url(instance.strands_url)

    class Meta:
        model = models.Curriculum
        fields = ["id", "grade", "subject", "strands"]


class StrandSerializer(serializers.ModelSerializer):
    substrands = serializers.SerializerMethodField()

    def get_substrands(self, instance):
        abs_url = self.context["request"].build_absolute_uri
        return abs_url(instance.substrands_url)

    class Meta:
        model = models.Strand
        fields = ["number", "name", "substrands"]


class SubstrandSerializer(serializers.ModelSerializer):
    content_standards = serializers.SerializerMethodField()

    def get_content_standards(self, instance):
        abs_url = self.context["request"].build_absolute_uri
        return abs_url(instance.content_standards_url)

    class Meta:
        model = models.SubStrand
        fields = ["number", "name", "content_standards"]


class ContentStandardSerializer(serializers.ModelSerializer):
    learning_indicators = serializers.SerializerMethodField()

    def get_learning_indicators(self, instance):
        abs_url = self.context["request"].build_absolute_uri
        return abs_url(instance.learning_indicators_url)

    class Meta:
        model = models.ContentStandard
        fields = ["number", "name", "learning_indicators"]


class LearningInidicatorSerializer(serializers.ModelSerializer):
    lessons = serializers.SerializerMethodField()

    def get_lessons(self, instance):
        abs_url = self.context["request"].build_absolute_uri
        return abs_url(instance.lessons_url)

    class Meta:
        model = models.LearningIndicator
        fields = ["number", "name", "lessons"]


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Lesson
        fields = ["number", "topic", "content"]


class MCAQuestionSerializer(serializers.ModelSerializer):
    choices = serializers.SerializerMethodField()
    

    def validate_answer(self, value):
        obj = self.context["view"].get_object()
        choice = obj.choices.filter(pk=value)
        if not choice.exists():
            raise serializers.ValidationError({"error": "Invalid choice"})
        return value

    def get_fields(self):
        fields = super().get_fields()
        method = self.context["request"].method
        if method == "PUT":
            return {"answer": serializers.CharField(write_only=True)}
        return fields

    def get_choices(self, instance):
        choices = instance.choices.all()
        question_choices = dict()
        for choice in choices:
            question_choices[choice.pk] = choice.text
        return question_choices

    class Meta:
        model = models.Question
        fields = ["id", "lesson", "text", "choices"]


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Question
        fields = "__all__"
