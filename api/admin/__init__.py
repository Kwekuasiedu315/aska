from . import user_admin
from django.contrib import admin

from api import models
from . import inlines


@admin.register(models.Subject)
class SubjectAdmin(admin.ModelAdmin):
    inlines = [inlines.CurriculumInline]
    list_display = ["name", "curriculums"]

    @admin.display()
    def curriculums(self, obj):
        return [x.grade for x in obj.curriculums.all()]


@admin.register(models.Strand)
class StrandAdmin(admin.ModelAdmin):
    list_display = ["name", "curriculum"]
    search_fields = ["name"]
    inlines = [inlines.SubStrandInline]


@admin.register(models.ContentStandard)
class ContentSandard(admin.ModelAdmin):
    inlines = [inlines.LearningIndicatorInline]


@admin.register(models.District)
class DistrictAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(models.School)
class SchoolAdmin(admin.ModelAdmin):
    search_fields = ["code", "name"]
    list_display = ["name", "district", "code"]
    autocomplete_fields = ["district"]
    fieldsets = (
        (
            "Basic Information",
            {"fields": ("name", "code", "owner", "email", "gender", "telephone")},
        ),
        (
            "Location Information",
            {"fields": ("district", "town", "digital_address", "location")},
        ),
        (
            "Other Information",
            {
                "fields": ("description", "date_established", "logo", "visible"),
            },
        ),
    )


admin.site.register(models.Lesson)
