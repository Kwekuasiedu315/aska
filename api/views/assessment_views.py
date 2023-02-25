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
            queryset = queryset.filter(question_type="mc")
        return queryset

    def get_serializer_class(self, *args, **kwargs):
        if self.action in ["multiple_choices", "multiple_choices_detail"]:
            return MCAQuestionSerializer
        return super().get_serializer_class(*args, **kwargs)

    @action(detail=False, methods=["get", "post"])
    def multiple_choices(self, *args, **kwargs):
        queryset = self.get_queryset()
        lizer = self.get_serializer(queryset, many=True)
        return Response(lizer.data)

    @action(
        detail=False, methods=["get", "put"], url_path="multiple_choices/(?P<pk>\d+)"
    )
    def multiple_choices_detail(self, request, *args, **kwargs):
        obj = self.get_object()
        lizer = self.get_serializer(obj)
        if request.method == "PUT":
            lizer = self.get_serializer(data=request.data)
            lizer.is_valid(raise_exception=True)
            answer = request.data.get("answer", None)
        return Response(lizer.data)
