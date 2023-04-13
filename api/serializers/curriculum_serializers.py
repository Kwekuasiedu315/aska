from rest_framework import serializers

from api.models.curriculum_models import (
    Curriculum,
    Strand,
    SubStrand,
    Lesson,
)


class LessonSerializer(serializers.ModelSerializer):
    subject = serializers.CharField(source="subject.name")
    strand = serializers.CharField(source="strand.name")
    substrand = serializers.CharField(source="substrand.name")
    url = serializers.SerializerMethodField()

    def get_url(self, instance):
        abs_url = self.context["request"].build_absolute_uri
        return abs_url(instance.url)

    def get_fields(self):
        fields = super().get_fields()
        action = self.context["view"].action
        view_obj = self.context["view"].get_queryset().first()
        if not isinstance(view_obj, Lesson):
            new_fields = {}
            new_fields["topic"] = fields.pop("topic")
            new_fields["url"] = fields.pop("url")
            fields = new_fields
        return fields

    class Meta:
        model = Lesson
        fields = [
            "number",
            "grade",
            "subject",
            "strand",
            "substrand",
            "topic",
            "content",
            "url",
        ]


class SubstrandSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True)

    class Meta:
        model = SubStrand
        fields = ["number", "name", "lessons"]


class StrandSerializer(serializers.ModelSerializer):
    substrands = SubstrandSerializer(many=True)

    class Meta:
        model = Strand
        fields = ["number", "name", "substrands"]


class CurriculumSerializer(serializers.ModelSerializer):
    strands = serializers.SerializerMethodField()
    subject = serializers.CharField(source="subject.name")

    def get_strands(self, instance):
        abs_url = self.context["request"].build_absolute_uri
        return abs_url(instance.strands_url)

    class Meta:
        model = Curriculum
        fields = ["id", "grade", "subject", "strands"]
