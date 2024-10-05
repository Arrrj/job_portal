from rest_framework import serializers

from apps.company.serializers import CompanyCreateSerializer
from apps.jobs.models import JobListing, JobApplication


class JobSerializer(serializers.ModelSerializer):
    company = CompanyCreateSerializer(read_only=True)

    class Meta:
        model = JobListing
        fields = '__all__'


class JobApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = ['id', 'job', 'resume', 'cover_letter', 'applied_at', 'status']
        read_only_fields = ['applied_at', 'status']
