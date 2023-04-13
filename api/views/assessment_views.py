from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from api.models.assessment_models import Question
from api.serializers.assessment_serializers import (
    QuestionSerializer,
    MCAQuestionSerializer,
)


class AssessmentViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ["multiple_choices", "multiple_choices_detail"]:
            return queryset.filter(question_type="mc")
        return queryset

    def get_serializer_class(self, *args, **kwargs):
        if self.action in ["multiple_choices", "multiple_choices_detail"]:
            return MCAQuestionSerializer
        return super().get_serializer_class(*args, **kwargs)

    @action(detail=False, methods=["get", "post"])
    def multiple_choices(self, *args, **kwargs):
        seriailizer = self.get_serializer(self.get_queryset(), many=True)
        return Response(seriailizer.data)

    @action(
        detail=False, methods=["get", "put"], url_path="multiple_choices/(?P<pk>\d+)"
    )
    def multiple_choices_detail(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        if request.method == "PUT":
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            answer = request.data.get("answer", None)
        return Response(serializer.data)
