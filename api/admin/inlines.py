from django.contrib import admin

from api.models import SubStrand, Curriculum


class CurriculumInline(admin.StackedInline):
    model = Curriculum
    extra = 1


class SubStrandInline(admin.StackedInline):
    extra = 1
    model = SubStrand


