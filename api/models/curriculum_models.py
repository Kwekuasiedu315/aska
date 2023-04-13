from django.db import models
from django.urls import reverse
from django.utils.text import slugify


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
        self.id = f"{self.grade}-{self.subject.name}".lower().replace(" ", "-")
        super().save(*args, **kwargs)

    @property
    def strands_url(self):
        return reverse("api:curriculums-detail", kwargs={"curriculum": self.pk})

    def __str__(self):
        return self.id


class Strand(models.Model):
    id = models.CharField(max_length=100, unique=True, primary_key=True, editable=False)
    number = models.PositiveSmallIntegerField()
    curriculum = models.ForeignKey(
        Curriculum, related_name="strands", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=225)

    def save(self, *args, **kwargs):
        self.id = f"{self.curriculum.id}.{self.number}"
        super().save(*args, **kwargs)

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

    def __str__(self):
        return f"{self.strand.id} {self.name}"


class Lesson(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, editable=False)
    grade = models.CharField(max_length=10, choices=GRADE_CHOICES, editable=False)
    strand = models.ForeignKey(Strand, on_delete=models.CASCADE, editable=False)
    substrand = models.ForeignKey(
        SubStrand, related_name="lessons", on_delete=models.CASCADE
    )
    number = models.PositiveSmallIntegerField()
    topic = models.CharField(max_length=1024)
    content = models.TextField()
    slug = models.SlugField(unique=True, editable=False)

    @property
    def url(self):
        return reverse(
            "api:curriculums-lesson",
            kwargs={
                "curriculum": self.strand.curriculum.id,
                "lesson": self.slug,
            },
        )

    def __str__(self):
        return f"{self.substrand.id} {self.topic}"

    def save(self, *args, **kwargs):
        self.strand = self.substrand.strand
        self.grade = self.strand.curriculum.grade
        self.subject = self.strand.curriculum.subject
        self.slug = slugify(
            f"{self.strand.number}-{self.substrand.number}-{self.number}-{self.topic}"
        )
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ["number", "subject", "grade"]
