from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets
from django_filters.rest_framework.backends import DjangoFilterBackend

from django.shortcuts import get_object_or_404, get_list_or_404

from .permissions import CurriculumPermission
from api.serializers.assessment_serializers import QuestionSerializer
from api.models.curriculum_models import Curriculum, Lesson, Strand
from api.models.assessment_models import Question
from api.serializers.curriculum_serializers import (
    CurriculumSerializer,
    StrandSerializer,
    LessonSerializer,
)
from api.filters import (
    DynamicFilterBackend,
    LessonFilter,
    CurriculumFilter,
    QuestionFilter,
)


class CurriculumViewSet(viewsets.ModelViewSet):
    permission_classes = [CurriculumPermission]
    queryset = Curriculum.objects.all()
    serializer_classes = {
        "list": CurriculumSerializer,
        "retrieve": StrandSerializer,
        "lessons": LessonSerializer,
        "lesson": LessonSerializer,
        "lesson_questions": QuestionSerializer,
    }
    lookup_url_kwarg = "curriculum"
    lookup_value_regex = "b\d+-\w+"
    filter_backends = [DynamicFilterBackend]
    filterset_classes = {
        "list": CurriculumFilter,
        "lessons": LessonFilter,
        "lesson_questions": QuestionFilter,
    }

    def get_serializer_class(self):
        if self.serializer_class:
            return self.serializer_class
        serializer = self.serializer_classes.get(self.action)
        assert (
            serializer is not None
        ), "Serializer is None, And None Type is not allowed"
        return serializer

    def retrieve(self, *args, **kwargs):
        queryset = Strand.objects.filter(curriculum_id=kwargs["curriculum"])
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, queryset=Lesson.objects.all())
    def lessons(self, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, queryset=Lesson.objects.all(), url_path="(?P<lesson>[^/.]+)")
    def lesson(self, *args, **kwargs):
        lesson = get_object_or_404(self.get_queryset(), slug=kwargs["lesson"])
        serializer = self.get_serializer(lesson)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["get", "post"],
        queryset=Question.objects.all(),
        url_path="(?P<lesson>[^/.]+)/questions",
    )
    def lesson_questions(self, request, **kwargs):
        questions = self.get_queryset().filter(lesson__slug=kwargs["lesson"])
        queryset = self.filter_queryset(questions)
        serializer = self.get_serializer(queryset, many=True)
        if request.method == "POST":
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.validated_data["lesson"] = Lesson.objects.get(
                slug=kwargs["lesson"]
            )
            serializer.save()
        return Response(serializer.data)
