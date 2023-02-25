from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import (
    UserProfileViewSet,
    SchoolProfileViewSet,
    CurriculumViewSet,
    AssessmentViewSet,
)

router = DefaultRouter()
router.register(r"users", UserProfileViewSet, basename="users")
router.register(r"schools", SchoolProfileViewSet, basename="schools")
router.register(r"curriculums", CurriculumViewSet, basename="curriculums")
router.register(r"assessments", AssessmentViewSet, basename="assessments")

app_name = "api"

urlpatterns = [
    path(r"", include(router.urls)),
]
