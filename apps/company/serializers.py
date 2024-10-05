from rest_framework import serializers

from apps.company.models import Company


class CompanyCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        exclude = ['owner']
