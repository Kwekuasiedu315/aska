from rest_framework import serializers
from rest_framework.authtoken.models import Token

from django.contrib.auth import authenticate

from .fields import user_field_list
from api.models.user_models import CHOICES, CustomUser, Friendship


class UserSerializer(serializers.ModelSerializer):
    gender = serializers.ChoiceField(choices=CHOICES["GENDER"], allow_blank=True)
    education_history = serializers.SerializerMethodField("get_education_history")
    level = serializers.ChoiceField(choices=CHOICES["LEVEL"], allow_blank=True)
    friendship_status = serializers.SerializerMethodField()
    url = serializers.HyperlinkedIdentityField(view_name="api:users-detail")

    @property
    def user(self):
        return self.context["request"].user

    @property
    def action(self):
        return self.context["view"].action

    @property
    def request(self):
        return self.context["request"]

    def get_friendship_status(self, instance):
        user = self.user
        if user.is_authenticated:
            return user.friendship_status(instance)

    def get_education_history(self, instance):
        education_history = instance.education_history.all()
        if instance.education_history:
            return [edu.school.name for edu in education_history]

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
        elif self.action == "update":
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
        fields = user_field_list
        model = CustomUser
        extra_kwargs = {
            "password": {"write_only": True},
            "points": {"read_only": True},
            "last_login": {"read_only": True},
            "date_joined": {"read_only": True},
        }


class FriendshipSerializer(serializers.ModelSerializer):
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
        model = Friendship
        fields = []
