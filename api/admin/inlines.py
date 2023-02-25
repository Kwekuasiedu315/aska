from django.contrib import admin

from api.models import SubStrand, Curriculum, LearningIndicator


class CurriculumInline(admin.StackedInline):
    model = Curriculum
    extra = 1


class SubStrandInline(admin.StackedInline):
    extra = 1
    model = SubStrand


class LearningIndicatorInline(admin.StackedInline):
    extra = 1
    model = LearningIndicator
