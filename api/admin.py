from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . import models


class CustomUserAdmin(UserAdmin):
    ordering = ("id",)
    fieldsets = (
        (None, {"fields": ("phone_number", "nickname")}),
        (
            "Personal Info",
            {
                "fields": (
                    "first_name",
                    "middle_name",
                    "last_name",
                    "email",
                    "gender",
                    "bio",
                )
            },
        ),
        (
            "School Info",
            {"fields": ("subjects", "level")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Photos", {"fields": ["profile_picture", "cover_picture"]}),
        ("Important Dates", {"fields": ("birthdate", "last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "phone_number",
                    "first_name",
                    "middle_name",
                    "last_name",
                    "birthdate",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    list_display = ["first_name", "last_name", "phone_number"]


admin.site.register(models.CustomUser, CustomUserAdmin)
admin.site.register(
    [
        models.Subject,
        models.FriendRequest,
        models.School,
        models.Education,
        models.Lesson,
        models.Question,
        models.MultipleChoiceAnswer,
        models.Choice,
    ]
)
