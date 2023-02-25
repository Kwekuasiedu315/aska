from django.db import models

from .curriculum_models import ContentStandard, Subject

QUESTION_TYPE_CHOICES = [
    ("MC", "Multiple Choice"),
    ("TF", "True or False"),
    ("SA", "Short Answer"),
]


class Question(models.Model):
    question_type = models.CharField(max_length=100, choices=QUESTION_TYPE_CHOICES)
    curriculum = models.ForeignKey(
        Subject, related_name="questions", on_delete=models.CASCADE, editable=False
    )
    lesson = models.ForeignKey(
        ContentStandard, related_name="questions", on_delete=models.CASCADE
    )
    text = models.TextField()

    def save(self, *args, **kwargs):
        self.curriculum = self.lesson.substrand.strand.curriculum
        super().save(self, *args, **kwargs)


class ShortAnswer(models.Model):
    text = models.CharField(max_length=255)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)


class MultipleChoiceAnswer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)


class TrueFalseAnswer(models.OneToOneField):
    question = models.OneToOneField(Question, on_delete=models.CASCADE)
    text = models.BooleanField(default=True)
