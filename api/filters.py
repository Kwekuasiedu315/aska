from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend

from api.models import Lesson, Curriculum, Question


class LessonFilter(filters.FilterSet):
    class Meta:
        model = Lesson
        fields = {
            "number": ["exact"],
            "grade": ["exact"],
            "subject": ["exact"],
            "subject__name": ["icontains"],
            "strand__name": ["icontains"],
            "substrand__name": ["icontains"],
            "topic": ["icontains"],
            "content": ["icontains"],
        }


class CurriculumFilter(filters.FilterSet):
    class Meta:
        model = Curriculum
        fields = ["grade", "subject"]


class QuestionFilter(filters.FilterSet):
    class Meta:
        model = Question
        fields = {
            "question_type": ["exact"],
            "text": ["icontains"],
            "lesson__topic": ["icontains"],
        }


class DynamicFilterBackend(DjangoFilterBackend):
    """
    A dynamic filter backend that sets the filterset class based on the view action.
    """

    def get_filterset_class(self, view, queryset=None):
        filterset_classes = getattr(view, "filterset_classes", None)
        assert (
            filterset_classes is not None
        ), "The 'DynamicFilterBackend' requires the view to have a 'filterset_classes' attribute."
        return filterset_classes.get(view.action)
