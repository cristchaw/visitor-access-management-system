from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "STUDENT", "Student"
        SECURITY = "SECURITY", "Security"
        ADMIN = "ADMIN", "Admin"

    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT,
    )
    phone = models.CharField(max_length=20, blank=True)
    student_id = models.CharField(
        max_length=30,
        unique=True,
        null=True,
        blank=True,
    )
    is_blocked = models.BooleanField(default=False)
    overdue_blocked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} ({self.role})"