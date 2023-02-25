from rest_framework import serializers

from api.models.assessment_models import Question


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = "__all__"


class MCAQuestionSerializer(serializers.ModelSerializer):
    choices = serializers.SerializerMethodField()

    def validate_answer(self, value):
        obj = self.context["view"].get_object()
        choice = obj.choices.filter(pk=value)
        if not choice.exists():
            raise serializers.ValidationError({"error": "Invalid choice"})
        return value

    def get_fields(self):
        fields = super().get_fields()
        method = self.context["request"].method
        if method == "PUT":
            return {"answer": serializers.CharField(write_only=True)}
        return fields

    def get_choices(self, instance):
        choices = instance.choices.all()
        question_choices = dict()
        for choice in choices:
            question_choices[choice.pk] = choice.text
        return question_choices

    class Meta:
        model = Question
        fields = ["id", "lesson", "text", "choices"]
