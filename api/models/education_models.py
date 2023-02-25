from django.db import models
from django.utils import timezone


REGION_CHOICES = [
    ("ASH", "Ashanti Region"),
    ("AHA", "Ahafo Region"),
    ("BON", "Bono East Region"),
    ("CEN", "Central Region"),
    ("EAS", "Eastern Region"),
    ("GRE", "Greater Accra Region"),
    ("NTN", "Northern Region"),
    ("NEA", "North East Region"),
    ("SVA", "Savannah Region"),
    ("UPW", "Upper West Region"),
    ("WES", "Western Region"),
    ("UPE", "Upper East Region"),
    ("VOL", "Volta Region"),
    ("WNO", "Western North Region"),
    ("OTI", "Oti Region"),
]
SCHOOL_TYPE_CHOICES = [
    ("M", "Mixed"),
    ("B", "Boys"),
    ("G", "Girls"),
]
SCHOOL_OWNER_CHOICES = [
    ("PVT", "Private"),
    ("GOV", "Government"),
]


class District(models.Model):
    name = models.CharField(max_length=100)
    region = models.CharField(choices=REGION_CHOICES, max_length=100)

    def __str__(self):
        return self.name


class School(models.Model):
    added_by = models.ForeignKey(
        "api.CustomUser",
        related_name="schools_added",
        on_delete=models.SET_NULL,
        editable=False,
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    owner = models.CharField(choices=SCHOOL_OWNER_CHOICES, max_length=50, default="gov")
    email = models.EmailField(null=True)
    gender = models.CharField(max_length=100, choices=SCHOOL_TYPE_CHOICES, default="M")
    telephone = models.ForeignKey(
        "api.Telephone",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    town = models.CharField(max_length=100)
    digital_address = models.CharField(max_length=100, null=True, blank=True)
    location = models.URLField(
        null=True, blank=True, help_text="School location on google map"
    )
    description = models.TextField(blank=True, null=True)
    date_established = models.DateField(blank=True, null=True)
    visible = models.BooleanField(
        default=True, help_text="Tick to show that the school is visible to users"
    )
    logo = models.ImageField(upload_to="school", default="defaults/cover.jpeg")

    def old_students(self):
        """Return the users who have completed the school"""

    def current_students(self):
        """Return the students who are present in the school"""

    def __str__(self):
        return self.name


class SchoolPicture(models.Model):
    school = models.ForeignKey(
        School, related_name="pictures", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="school/images")
    caption = models.CharField(max_length=225)
    timestamp = models.DateTimeField(auto_now=True)


class SchoolFeed(models.Model):
    text = models.TextField()
    image = models.ImageField(upload_to="school/feeds", blank=True, null=True)
    school = models.ForeignKey(School, related_name="feeds", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True, editable=False)


class EducationHistory(models.Model):
    user = models.ForeignKey(
        "api.CustomUser", related_name="education_history", on_delete=models.CASCADE
    )
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    date_started = models.DateField(blank=True, null=True)
    date_completed = models.DateField(blank=True, null=True)

    def user_present(self):
        if self.date_completed:
            return True if self.date_completed < timezone.now() else False
        return None

    def __str__(self):
        return f"{self.user.first_name} {self.school.name}"


CHOICES = {
    "SCHOOL_OWNER": SCHOOL_OWNER_CHOICES,
    "SCHOOL_TYPE": SCHOOL_TYPE_CHOICES,
}
