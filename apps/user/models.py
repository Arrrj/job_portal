from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('candidate', 'candidate'),
        ('employer', 'employer'),
    )
    roles = models.CharField(max_length=10, choices=ROLE_CHOICES)
    email = models.EmailField(unique=True)

    first_name = None
    last_name = None
    date_joined = None
    last_login = None

    def __str__(self):
        return self.username
