from rest_framework import viewsets, serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.company.models import Company
from apps.company.serializers import CompanyCreateSerializer
from apps.permissions import IsEmployer


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanyCreateSerializer
    permission_classes = [IsAuthenticated, IsEmployer]

    def create(self, request):
        if Company.objects.filter(owner=request.user).exists():
            return Response({'message': 'User already owns a company.'}, status=status.HTTP_409_CONFLICT)

        data = request.data.copy()
        data['owner'] = request.user.id
        serializer = CompanyCreateSerializer(data=data)

        company_name = data.get('company_name')
        if Company.objects.filter(company_name=company_name).exists():
            return Response({'message': 'Company Name already exists'}, status=status.HTTP_409_CONFLICT)

        if serializer.is_valid():
            serializer.save(owner=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
