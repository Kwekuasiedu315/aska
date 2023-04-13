from django.db import models

from .curriculum_models import Lesson, Subject

QUESTION_TYPE_CHOICES = [
    ("MC", "Multiple Choice"),
    ("TF", "True or False"),
    ("SA", "Short Answer"),
]


class Question(models.Model):
    question_type = models.CharField(max_length=100, choices=QUESTION_TYPE_CHOICES)
    lesson = models.ForeignKey(
        Lesson, related_name="questions", on_delete=models.CASCADE
    )
    text = models.TextField()


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
