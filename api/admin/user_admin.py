from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from api.models import CustomUser, EducationHistory


class EducationHistoryIinline(admin.StackedInline):
    model = EducationHistory
    extra = 1


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    inlines = [EducationHistoryIinline]
    ordering = ("id",)
    readonly_fields = ("last_login", "date_joined")
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
            {"fields": ("school", "subjects", "level")},
        ),
        ("Photos", {"fields": ["profile_picture", "cover_picture"]}),
        ("Important Dates", {"fields": ("birthdate", "last_login", "date_joined")}),
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
                "classes": ("collapse",),
            },
        ),
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

    def has_change_permission(self, request, obj=None):
        if obj is not None:
            return obj == request.user
        return super().has_change_permission(request, obj)
