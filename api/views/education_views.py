from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets

from django.db.models import Q
from django.shortcuts import get_object_or_404

from api.models.education_models import School
from api.serializers.education_serializers import (
    SchoolSerializer,
    SchoolFeedSerializer,
    SchoolPictureSerializer,
)


class SchoolProfileViewSet(viewsets.ModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer

    def get_serializer_class(self):
        if self.action == "pictures":
            return SchoolPictureSerializer
        elif self.action == "feeds":
            return SchoolFeedSerializer
        return super().get_serializer_class()

    @action(detail=True, methods=["get", "post"])
    def pictures(self, request, *args, **kwargs):
        queryset = self.get_object().pictures.all()
        lizer = self.get_serializer(queryset, many=True)
        if request.method == "POST":
            lizer = self.get_serializer(data=request.data)
            lizer.is_valid(raise_exception=True)
            lizer.save()
        return Response(lizer.data)

    @action(detail=True, methods=["get", "post"])
    def feeds(self, request, *args, **kwargs):
        queryset = self.get_object().feeds.all()
        lizer = self.get_serializer(queryset, many=True)
        if request.method == "POST":
            lizer = self.get_serializer(data=request.data)
            lizer.is_valid(raise_exception=True)
            lizer.save()
        return Response(lizer.data)
