from rest_framework.routers import DefaultRouter
from django.urls import path, include

from . import views

router = DefaultRouter()
router.register(r"users", views.UserProfileViewSet, basename="user")
router.register(r"school", views.SchoolProfileViewSet, basename="school")
router.register(r"curriculum", views.CurriculumViewSet, basename="curriculum")
router.register(r"questions", views.QuestionViewSet, basename="questions")

app_name = "api"

urlpatterns = [
    path(r"", include(router.urls)),
]
