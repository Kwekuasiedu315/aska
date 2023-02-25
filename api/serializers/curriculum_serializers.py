from rest_framework import serializers

from api.models.curriculum_models import (
    Curriculum,
    Strand,
    SubStrand,
    ContentStandard,
    LearningIndicator,
    Lesson,
)


class CurriculumSerializer(serializers.ModelSerializer):
    strands = serializers.SerializerMethodField()

    def get_strands(self, instance):
        abs_url = self.context["request"].build_absolute_uri
        return abs_url(instance.strands_url)

    class Meta:
        model = Curriculum
        fields = ["id", "grade", "subject", "strands"]


class StrandSerializer(serializers.ModelSerializer):
    substrands = serializers.SerializerMethodField()

    def get_substrands(self, instance):
        abs_url = self.context["request"].build_absolute_uri
        return abs_url(instance.substrands_url)

    class Meta:
        model = Strand
        fields = ["number", "name", "substrands"]


class SubstrandSerializer(serializers.ModelSerializer):
    content_standards = serializers.SerializerMethodField()

    def get_content_standards(self, instance):
        abs_url = self.context["request"].build_absolute_uri
        return abs_url(instance.content_standards_url)

    class Meta:
        model = SubStrand
        fields = ["number", "name", "content_standards"]


class ContentStandardSerializer(serializers.ModelSerializer):
    learning_indicators = serializers.SerializerMethodField()

    def get_learning_indicators(self, instance):
        abs_url = self.context["request"].build_absolute_uri
        return abs_url(instance.learning_indicators_url)

    class Meta:
        model = ContentStandard
        fields = ["number", "name", "learning_indicators"]


class LearningInidicatorSerializer(serializers.ModelSerializer):
    lessons = serializers.SerializerMethodField()

    def get_lessons(self, instance):
        abs_url = self.context["request"].build_absolute_uri
        return abs_url(instance.lessons_url)

    class Meta:
        model = LearningIndicator
        fields = ["number", "name", "lessons"]


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["number", "topic", "content"]
