from django.db import models
from django.contrib.auth.models import AbstractUser
from studentportal.managers import CustomUserManager
import uuid

YEARS = (
    ("first", "First Year"),
    ("second", "Second Year"),
    ("third", "Third Year"),
    ("fourth", "Fourth Year")
)

JOB_TYPE = (
    ("internship", "Internship"),
    ("placement", "Placement")
)

HACKATHON_CERTIFICATE_TYPE = (
    ("winner", "Winner"),
    ("first_runner", "First Runner"),
    ("second_runner", "Second Runner"),
    ("special_mentioned", "Special Mentioned"),
    ("top_five", "Top 5"),
    ("top_ten", "Top 10"),
    ("top_fifty", "Top 50"),
    ("top_fifty", "Top 50"),
    ("participant", "Participant"),
    ("other", "Other")
)

MONTHS = (
    ("1", "January"),
    ("2", "February"),
    ("3", "March"),
    ("4", "April"),
    ("5", "May"),
    ("6", "June"),
    ("7", "July"),
    ("8", "August"),
    ("9", "September"),
    ("10", "October"),
    ("11", "November"),
    ("12", "December"),
)


class StudentAuthProfile(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50, null=True)
    last_name = models.CharField(max_length=50, null=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]
    objects = CustomUserManager()

    def __str__(self):
        return str(self.get_full_name())


class StudentPersonalProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(StudentAuthProfile, on_delete=models.CASCADE, related_name="personal_profile")
    roll_no = models.CharField(max_length=20, null=True)
    phone_no = models.CharField(max_length=20, null=True)

    year = models.CharField(max_length=20, choices=YEARS, default="first")
    graduation_year = models.CharField(max_length=20, default="2026")
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user.get_full_name()) + " - " + self.roll_no


class JobProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(StudentAuthProfile, on_delete=models.CASCADE, related_name="job_profile")
    type = models.CharField(max_length=20, choices=JOB_TYPE, default="internship")
    duration_months = models.IntegerField(default=0)
    company = models.TextField(default="")
    month = models.CharField(default="1", choices=MONTHS, max_length=10)
    year = models.IntegerField(default=2022)
    document = models.TextField(null=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user.get_full_name()) + " - " + self.get_type_display() + " - " + self.company


class HackathonProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(StudentAuthProfile, on_delete=models.CASCADE, related_name="hackathon_profile")
    title = models.TextField(default="")
    organizer = models.CharField(max_length=250, default="")
    certificate_type = models.CharField(max_length=50, choices=HACKATHON_CERTIFICATE_TYPE, default="winner")
    month = models.CharField(default="1", choices=MONTHS, max_length=10)
    year = models.IntegerField(default=2022)
    document = models.TextField(null=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user.get_full_name()) + " - " + self.organizer + " - " + self.get_certificate_type_display()


class OnlineCoursesProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(StudentAuthProfile, on_delete=models.CASCADE, related_name="online_courses_profile")
    title = models.TextField(default="")
    issued_by = models.TextField(default="")
    description = models.TextField(default="")  # Description may include link
    year = models.IntegerField(default=2022)
    document = models.TextField(null=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user.get_full_name()) + " - " + self.title + " - " + self.issued_by

class OtherDocuments(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(StudentAuthProfile, on_delete=models.CASCADE, related_name="other_documents")
    title = models.TextField(default="")
    description = models.TextField(default="")
    document = models.TextField(null=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user.get_full_name()) + " - " + self.title
