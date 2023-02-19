from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone

import random
from . import choices
from .managers import CustomUserManager


class FriendRequest(models.Model):
    sender = models.ForeignKey(
        "CustomUser", on_delete=models.CASCADE, related_name="sent_friend_requests"
    )
    receiver = models.ForeignKey(
        "CustomUser", on_delete=models.CASCADE, related_name="received_friend_requests"
    )
    status = models.CharField(
        max_length=10, choices=choices.REQUEST_STATUS, default="pending"
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.first_name} {self.sender.id} -->> {self.receiver.first_name} {self.receiver.id}"


class CustomUser(AbstractUser):
    # Phone number field to use as the unique identifier of the user
    username = None
    nickname = models.CharField(max_length=20, blank=True, null=True)
    phone_number = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    gender = models.CharField(choices=choices.GENDER, max_length=20)
    birthdate = models.DateField()
    bio = models.TextField(max_length=200, blank=True, null=True)
    level = models.CharField(max_length=100, choices=choices.LEVEL, blank=True)
    subjects = models.ManyToManyField("Subject", related_name="users", blank=True)
    points = models.IntegerField(default=0)
    password_reset_code = models.CharField(editable=False, null=True, max_length=100)
    profile_picture = models.ImageField(upload_to="users", default="defaults/user.png")
    cover_picture = models.ImageField(upload_to="users", default="defaults/cover.jpeg")

    friend_requests = models.ManyToManyField(
        "self", through=FriendRequest, symmetrical=True
    )

    USERNAME_FIELD = "phone_number"

    objects = CustomUserManager()

    REQUIRED_FIELDS = [
        "first_name",
        "middle_name",
        "last_name",
        "gender",
        "birthdate",
    ]

    @property
    def full_name(self):
        """Combine first, middle, and last name to create full name"""
        names = (self.first_name, self.middle_name, self.last_name)
        return " ".join((name for name in names if name))

    @property
    def current_school(self):
        """Return the current school of the user"""
        return self.school.first().school if self.school.first() else None

    @property
    def educations(self):
        """Return a queryset of all the schools the user has attended"""
        return self.school.all()

    @property
    def friends(self):
        return FriendRequest.objects.filter(
            models.Q(sender=self) | models.Q(receiver=self), status="accepted"
        )

    @property
    def url(self):
        """Return the URL for the user's detail page"""
        return reverse("api:user-detail", kwargs={"phone_number": self.phone_number})

    def friend_request_status(self, user):
        friend_request = FriendRequest.objects.filter(
            models.Q(sender=self, receiver=user) | models.Q(receiver=self, sender=user)
        ).first()
        if friend_request:
            if friend_request.status == "accepted":
                return "accepted"
            elif friend_request.sender == self:
                return "sent"
            elif friend_request.receiver == self:
                return "received"
        return None

    def reset_password(self):
        code = str(random.randint(10000, 1000000))
        self.password_reset_code = code
        self.save()
        return code

    def __str__(self):
        return f"{self.first_name} ({self.id})"


class District(models.Model):
    name = models.CharField(max_length=100)
    region = models.CharField(choices=choices.REGION, max_length=100)


class School(models.Model):
    added_by = models.ForeignKey(
        CustomUser,
        related_name="schools_added",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=200)
    index = models.CharField(help_text="Index Number", max_length=20, unique=True)
    owner = models.CharField(choices=choices.SCHOOL_OWNER, max_length=50, default="gov")
    email = models.EmailField(null=True)
    gender = models.CharField(max_length=100, choices=choices.SCHOO_TYPE)
    telephone = models.ForeignKey(
        "Telephone",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    visible = models.BooleanField(default=False)
    address = models.URLField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    date_established = models.DateField(blank=True, null=True)
    logo = models.ImageField(upload_to="school", default="defaults/cover.jpeg")

    def __str__(self):
        return self.name

    def old_students(self):
        """Return the users who have completed the school"""

    def current_students(self):
        """Return the students who are present in the school"""


class Education(models.Model):
    user = models.ForeignKey(
        "CustomUser", related_name="school", on_delete=models.CASCADE
    )
    school = models.ForeignKey("School", on_delete=models.CASCADE)
    date_started = models.DateField(blank=True, null=True)
    date_completed = models.DateField(blank=True, null=True)

    def user_present(self):
        if self.date_completed:
            return True if self.date_completed < timezone.now() else False
        return None


class Telephone(models.Model):
    number = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.number


class Subject(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Curriculum(models.Model):
    id = models.CharField(max_length=100, primary_key=True, editable=False)
    grade = models.CharField(max_length=10, choices=choices.GRADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.pk = f"{self.subject.name}-{self.grade}".lower().replace(" ", "-")
        super().save(*args, **kwargs)

    @property
    def strands_url(self):
        return reverse("api:curriculum-detail", kwargs={"curriculum": self.id})

    def __str__(self):
        return self.id

    class Meta:
        unique_together = ["grade", "subject"]


class Strand(models.Model):
    number = models.SmallIntegerField()
    curriculum = models.ForeignKey(
        Curriculum, related_name="strand", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.curriculum.grade} {self.name}"

    @property
    def substrands_url(self):
        return self.curriculum.strands_url + str(self.number) + "/"


class SubStrand(models.Model):
    number = models.SmallIntegerField()
    strand = models.ForeignKey(
        Strand, related_name="substrand", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)

    @property
    def content_standards_url(self):
        return self.strand.substrands_url + str(self.number) + "/"

    def __str__(self):
        return f"{self.strand.curriculum.grade} {self.name}"


class ContentStandard(models.Model):
    number = models.SmallIntegerField()
    substrand = models.ForeignKey(
        SubStrand, related_name="content_standard", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=500)

    @property
    def learning_indicators_url(self):
        return self.substrand.content_standards_url + str(self.number) + "/"

    def __str__(self):
        return f"{self.substrand.strand.curriculum.grade} {self.name}"


class LearningIndicator(models.Model):
    number = models.SmallIntegerField()
    content_standard = models.ForeignKey(
        ContentStandard, related_name="learning_indicator", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=500)

    @property
    def lessons_url(self):
        return self.content_standard.learning_indicators_url + str(self.number) + "/"

    def __str__(self):
        return f"{self.content_standard.substrand.strand.curriculum.grade} {self.name}"


class Lesson(models.Model):
    number = models.PositiveSmallIntegerField()
    grade = models.CharField(max_length=10, editable=False)
    subject = models.ForeignKey(
        Subject, related_name="lesson", on_delete=models.CASCADE, editable=False
    )
    strand = models.ForeignKey(
        Strand, related_name="lesson", on_delete=models.CASCADE, editable=False
    )
    substrand = models.ForeignKey(
        SubStrand, related_name="lesson", on_delete=models.CASCADE, editable=False
    )
    content_standard = models.ForeignKey(
        ContentStandard, related_name="lesson", on_delete=models.CASCADE, editable=False
    )
    learning_indicator = models.ForeignKey(
        LearningIndicator, related_name="lesson", on_delete=models.CASCADE
    )
    topic = models.CharField(max_length=1024)
    content = models.TextField()

    def __str__(self):
        return f"{self.grade}.{self.strand.number}.{self.substrand.number}.{self.content_standard.number}.{self.learning_indicator.number} {self.topic}"

    def save(self, *args, **kwargs):
        self.content_standard = self.learning_indicator.content_standard
        self.substrand = self.content_standard.substrand
        self.strand = self.substrand.strand
        self.grade = self.strand.curriculum.grade
        self.subject = self.strand.curriculum.subject
        super().save(*args, **kwargs)


class Question(models.Model):
    question_type = models.CharField(max_length=100, choices=choices.QUESTION_TYPE)
    lesson = models.ForeignKey(
        ContentStandard, related_name="questions", on_delete=models.CASCADE
    )
    text = models.TextField()


class Choice(models.Model):
    question = models.ForeignKey(
        Question, related_name="choices", on_delete=models.CASCADE
    )
    text = models.CharField(max_length=500)
    correct = models.BooleanField(default=False)


class TrueFalseAnswer(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="true_false_answers"
    )
    answer = models.BooleanField()
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("question", "user")


class MultipleChoiceAnswer(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="multiple_choice_answers"
    )
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("question", "user")


class ShortAnswer(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="short_answers"
    )
    answer = models.CharField(max_length=225)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("question", "user")


class LongAnswer(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="long_answers"
    )
    answer = models.TextField()
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("question", "user")
