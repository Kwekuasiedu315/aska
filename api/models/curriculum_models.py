from django.db import models
from django.urls import reverse


GRADE_CHOICES = [
    ("B4", "B4"),
    ("B5", "B5"),
    ("B6", "B6"),
]


class Subject(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Curriculum(models.Model):
    id = models.CharField(max_length=100, primary_key=True, unique=True, editable=False)
    grade = models.CharField(max_length=10, choices=GRADE_CHOICES)
    subject = models.ForeignKey(
        Subject, related_name="curriculums", on_delete=models.CASCADE
    )

    def save(self, *args, **kwargs):
        self.id = f"{self.subject.name}-{self.grade}".lower().replace(" ", "-")
        super().save(*args, **kwargs)

    @property
    def strands_url(self):
        return reverse("api:curriculums-detail", kwargs={"curriculum": self.id})

    def __str__(self):
        return self.id


class Strand(models.Model):
    id = models.CharField(max_length=100, unique=True, primary_key=True, editable=False)
    number = models.PositiveSmallIntegerField()
    curriculum = models.ForeignKey(
        Curriculum, related_name="strands", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        self.id = f"{self.curriculum.id}.{self.number}"
        super().save(*args, **kwargs)

    @property
    def substrands_url(self):
        return self.curriculum.strands_url + str(self.number) + "/"

    def __str__(self):
        return f"{self.curriculum.id} {self.name}"


class SubStrand(models.Model):
    id = models.CharField(max_length=100, unique=True, primary_key=True, editable=False)
    number = models.PositiveSmallIntegerField()
    strand = models.ForeignKey(
        Strand, related_name="substrands", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        self.id = f"{self.strand.id}.{self.number}"
        super().save(*args, **kwargs)

    @property
    def content_standards_url(self):
        return self.strand.substrands_url + str(self.number) + "/"

    def __str__(self):
        return f"{self.strand.id} {self.name}"


class ContentStandard(models.Model):
    id = models.CharField(max_length=100, unique=True, primary_key=True, editable=False)
    number = models.PositiveSmallIntegerField()
    substrand = models.ForeignKey(
        SubStrand, related_name="content_standards", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=500)

    def save(self, *args, **kwargs):
        self.id = f"{self.substrand.id}.{self.number}"
        super().save(*args, **kwargs)

    @property
    def learning_indicators_url(self):
        return self.substrand.content_standards_url + str(self.number) + "/"

    def __str__(self):
        return f"{self.substrand.id} {self.name}"


class LearningIndicator(models.Model):
    id = models.CharField(max_length=100, unique=True, primary_key=True, editable=False)
    number = models.PositiveSmallIntegerField()
    content_standard = models.ForeignKey(
        ContentStandard, related_name="learning_indicators", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=500)

    def save(self, *args, **kwargs):
        self.id = f"{self.content_standard.id}.{self.number}"
        super().save(*args, **kwargs)

    @property
    def lessons_url(self):
        return self.content_standard.learning_indicators_url + str(self.number) + "/"

    def __str__(self):
        return f"{self.content_standard.id} {self.name}"


class Lesson(models.Model):
    id = models.CharField(max_length=100, unique=True, primary_key=True, editable=False)
    number = models.PositiveSmallIntegerField()
    curriculum = models.ForeignKey(
        Curriculum, related_name="lessons", on_delete=models.CASCADE, editable=False
    )
    strand = models.ForeignKey(
        Strand, related_name="lessons", on_delete=models.CASCADE, editable=False
    )
    substrand = models.ForeignKey(
        SubStrand, related_name="lessons", on_delete=models.CASCADE, editable=False
    )
    content_standard = models.ForeignKey(
        ContentStandard,
        related_name="lessons",
        on_delete=models.CASCADE,
        editable=False,
    )
    learning_indicator = models.ForeignKey(
        LearningIndicator, related_name="lessons", on_delete=models.CASCADE
    )
    topic = models.CharField(max_length=1024)
    content = models.TextField()

    def __str__(self):
        return f"{self.learning_indicator} {self.topic}"

    def save(self, *args, **kwargs):
        self.content_standard = self.learning_indicator.content_standard
        self.substrand = self.content_standard.substrand
        self.strand = self.substrand.strand
        self.curriculum = self.strand.curriculum
        super().save(*args, **kwargs)
