from django.db import models

from apps.user.models import User


class Company(models.Model):
    company_name = models.CharField(max_length=100)
    company_location = models.CharField(max_length=100)
    description = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, unique=True)
