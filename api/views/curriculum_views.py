from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets

from django.db.models import Q
from django.shortcuts import get_object_or_404

from api.models.curriculum_models import (
    Curriculum,
    Strand,
    SubStrand,
    ContentStandard,
    LearningIndicator,
    Lesson,
)
from api.serializers.assessment_serializers import QuestionSerializer
from api.serializers.curriculum_serializers import (
    CurriculumSerializer,
    StrandSerializer,
    SubstrandSerializer,
    ContentStandardSerializer,
    LearningInidicatorSerializer,
    LessonSerializer,
)


class CurriculumViewSet(viewsets.ModelViewSet):
    queryset = Curriculum.objects.all()
    lookup_field = "id"
    lookup_url_kwarg = "curriculum"

    def get_queryset(self):
        queryset = self.queryset
        curriculum = self.kwargs.get("curriculum", None)
        strand = self.kwargs.get("strand", None)
        substrand = self.kwargs.get("substrand", None)
        content_standard = self.kwargs.get("content_standard", None)
        learning_indicator = self.kwargs.get("learning_indicator", None)
        lesson = self.kwargs.get("lesson", None)
        if curriculum:
            queryset = get_object_or_404(queryset, id=curriculum).strand.all()
            if strand:
                queryset = get_object_or_404(queryset, number=strand).substrand.all()
                if substrand:
                    queryset = get_object_or_404(
                        queryset, number=substrand
                    ).content_standard.all()
                    if content_standard:
                        queryset = get_object_or_404(
                            queryset, number=content_standard
                        ).learning_indicator.all()
                        if learning_indicator:
                            queryset = get_object_or_404(
                                queryset, number=learning_indicator
                            ).lesson.all()
                            if lesson:
                                queryset = get_object_or_404(queryset, number=lesson)
        return queryset

    def get_serializer_class(self):
        if self.action in ("strands", "strands_all"):
            return StrandSerializer
        elif self.action in ("substrands", "substrands_all"):
            return SubstrandSerializer
        elif self.action in ("content_standards", "content_standards_all"):
            return ContentStandardSerializer
        elif self.action in ("learning_indicators", "learning_indicators_all"):
            return LearningInidicatorSerializer
        elif self.action in ("lessons", "lessons_all"):
            return LessonSerializer
        elif self.action == "questions":
            return QuestionSerializer
        return CurriculumSerializer

    @action(detail=False, url_path="strands")
    def strands_all(self, request, *args, **kwargs):
        queryset = Strand.objects.all()
        lizer = self.get_serializer(queryset, many=True)
        return Response(lizer.data)

    @action(detail=False, url_path="substrands")
    def substrands_all(self, request, *args, **kwargs):
        queryset = SubStrand.objects.all()
        lizer = self.get_serializer(queryset, many=True)
        return Response(lizer.data)

    @action(detail=False, url_path="content_standards")
    def content_standards_all(self, request, *args, **kwargs):
        queryset = ContentStandard.objects.all()
        lizer = self.get_serializer(queryset, many=True)
        return Response(lizer.data)

    @action(detail=False, url_path="learning_indicators")
    def learning_indicators_all(self, request, *args, **kwargs):
        queryset = LearningIndicator.objects.all()
        lizer = self.get_serializer(queryset, many=True)
        return Response(lizer.data)

    @action(detail=False, url_path="lessons")
    def lessons_all(self, request, *args, **kwargs):
        queryset = Lesson.objects.all()
        lizer = self.get_serializer(queryset, many=True)
        return Response(lizer.data)

    @action(detail=False, url_path="(?P<curriculum>^[a-z]+-[a-z]+\d+$)")
    def strands(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        lizer = self.get_serializer(queryset, many=True)
        return Response(lizer.data)

    @action(detail=True, url_path="(?P<strand>\d+)")
    def substrands(self, *args, **kwargs):
        queryset = self.get_queryset()
        lizer = self.get_serializer(queryset, many=True)
        return Response(lizer.data)

    @action(
        detail=True,
        url_path="(?P<strand>\d+)/(?P<substrand>\d+)",
    )
    def content_standards(self, *args, **kwargs):
        queryset = self.get_queryset()
        lizer = self.get_serializer(queryset, many=True)
        return Response(lizer.data)

    @action(
        detail=True,
        url_path="(?P<strand>\d+)/(?P<substrand>\d+)/(?P<content_standard>\d+)",
    )
    def learning_indicators(self, *args, **kwargs):
        queryset = self.get_queryset()
        lizer = self.get_serializer(queryset, many=True)
        return Response(lizer.data)

    @action(
        detail=True,
        methods=["get", "post"],
        url_path="(?P<strand>\d+)/(?P<substrand>\d+)/(?P<content_standard>\d+)/questions",
    )
    def questions(self, request, *args, **kwargs):
        number = self.kwargs["content_standard"]
        substrand_number = self.kwargs["substrand"]
        lesson = models.ContentStandard.objects.get(
            number=number, substrand__number=substrand_number
        )
        queryset = lesson.questions.all()
        lizer = self.get_serializer(queryset, many=True)
        if request.method == "POST":
            lizer = self.get_serializer(data=request.data)
            lizer.is_valid(raise_exception=True)
            lizer.validated_data["lesson"] = lesson
            lizer.save()
        return Response(lizer.data)

    @action(
        detail=True,
        url_path="(?P<strand>\d+)/(?P<substrand>\d+)/(?P<content_standard>\d+)/(?P<learning_indicator>\d+)",
    )
    def lessons(self, *args, **kwargs):
        queryset = self.get_queryset()
        lizer = self.get_serializer(queryset, many=True)
        return Response(lizer.data)
