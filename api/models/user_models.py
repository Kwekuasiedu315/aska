from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
import random
from django.core.files import File

from .managers import CustomUserManager
from api.utils import create_text_image

GENDER_CHOICES = [
    ("M", "Male"),
    ("F", "Female"),
]
LEVEL_CHOICES = [
    ("UPP", "Upper Primary"),
    ("JHS", "Junior High"),
    ("SHS", "Senior High"),
]
REQUEST_STATUS_CHOICES = [
    ("pending", "Pending"),
    ("accepted", "Accepted"),
    ("declined", "Declined"),
]


class Telephone(models.Model):
    number = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.number


class CustomUser(AbstractUser):
    # Phone number field to use as the unique identifier of the user
    username = None
    nickname = models.CharField(max_length=20, blank=True, null=True)
    phone_number = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=20)
    birthdate = models.DateField()
    school = models.ForeignKey(
        "api.School",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    bio = models.TextField(max_length=200, blank=True, null=True)
    level = models.CharField(max_length=100, choices=LEVEL_CHOICES, blank=True)
    subjects = models.ManyToManyField("api.Subject", related_name="users", blank=True)
    points = models.IntegerField(default=0)
    password_reset_code = models.CharField(editable=False, null=True, max_length=100)
    profile_picture = models.ImageField(upload_to="users", blank=True, null=True)
    cover_picture = models.ImageField(upload_to="users", blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.profile_picture:
            # Generate profile picture using user's initials
            initials = self.first_name[0] + self.last_name[0]
            image_path = create_text_image(initials, 150, 150)

            # Save generated image to profile_picture field
            with open(image_path, "rb") as f:
                file_name = f"{self.phone_number}.png"
                self.profile_picture.save(file_name, File(f), save=False)

        super().save(*args, **kwargs)

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
    def friends(self):
        """Return the user's friends"""
        friendship = Friendship.objects.filter(
            models.Q(sender=self) | models.Q(receiver=self),
            status="accepted",
        )
        related_user_ids = list(*friendship.values_list("sender", "receiver"))
        return self.__class__.objects.filter(id__in=related_user_ids, id__ne=self.id)

    @property
    def url(self):
        """Return the URL for the user's detail page"""
        return reverse("api:users-detail", kwargs={"pk": self.pk})

    def friendship_status(self, user):
        friendship = Friendship.objects.filter(
            models.Q(sender=self, receiver=user) | models.Q(receiver=self, sender=user)
        ).first()
        if friendship:
            if friendship.status == "accepted":
                return "accepted"
            elif friendship.sender == self:
                return "sent"
            elif friendship.receiver == self:
                return "received"
        return None

    def reset_password(self):
        code = str(random.randint(10000, 1000000))
        self.password_reset_code = code
        self.save()
        return code

    def __str__(self):
        return f"{self.first_name} ({self.id})"


class Friendship(models.Model):
    sender = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="sent_friend_requests"
    )
    receiver = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="received_friend_requests"
    )
    status = models.CharField(
        max_length=10, choices=REQUEST_STATUS_CHOICES, default="pending"
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.first_name} {self.sender.id} -->> {self.receiver.first_name} {self.receiver.id}"


CHOICES = {
    "GENDER": GENDER_CHOICES,
    "LEVEL": LEVEL_CHOICES,
    "REQUEST_STATUS": REQUEST_STATUS_CHOICES,
}
