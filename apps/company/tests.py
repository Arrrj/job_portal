from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from apps.company.models import Company
from apps.user.models import User


class CompanyViewSetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123',
            email='testuser@example.com',
            roles='employer'
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse('company-list')

    def test_create_company_success(self):
        data = {
            'company_name': 'Test Company',
            'company_location': 'Test Location',
            'description': 'This is a test company description.'
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Company.objects.count(), 1)
        self.assertEqual(Company.objects.get().company_name, 'Test Company')

    def test_create_company_already_owns(self):
        Company.objects.create(
            company_name='Existing Company',
            company_location='Existing Location',
            description='This is an existing company.',
            owner=self.user
        )

        data = {
            'company_name': 'New Company',
            'company_location': 'New Location',
            'description': 'This is a new company description.'
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data, {'message': 'User already owns a company.'})

    def test_create_company_invalid_data(self):
        data = {
            'company_name': '',
            'company_location': 'Test Location',
            'description': 'This is a test company description.'
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('company_name', response.data)

