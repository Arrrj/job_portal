from django.db import models

from apps.company.models import Company
from apps.user.models import User


class JobListing(models.Model):
    job_title = models.CharField(max_length=200)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    job_description = models.TextField()
    job_location = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'pending'),
        ('accepted', 'accepted'),
        ('rejected', 'rejected'),
    ]
    job = models.ForeignKey(JobListing, on_delete=models.CASCADE)
    candidate = models.ForeignKey(User, on_delete=models.CASCADE)
    resume = models.FileField()
    cover_letter = models.TextField(blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
