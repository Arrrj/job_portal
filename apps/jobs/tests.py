from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.company.models import Company
from apps.jobs.models import JobListing
from apps.user.models import User


class JobViewSetCreateTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123',
            email='testuser@example.com',
            roles='employer'
        )

        self.company = Company.objects.create(
            company_name="Ola",
            company_location= "Trissur",
            description="Commpany jkjkfjkdbasjdjckdjkdjed huwhdiuehduehdu",
            owner=self.user
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse('job-list')

    def test_create_job_success(self):
        data = {
            "job_title": "developer",
            "job_description": "kwdwkdlkdl",
            "job_location": "kochi",
            "salary": "24000"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(JobListing.objects.count(), 1)

    def test_company_not_found(self):
        data = {
            "job_title": "developer",
            "job_description": "kwdwkdlkdl",
            "job_location": "kochi",
            "salary": "24000"
        }
        self.company.delete()
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class JobViewSetUpdateTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123',
            email='testuser@example.com',
            roles='employer'
        )

        self.company = Company.objects.create(
            company_name="Ola",
            company_location="Trissur",
            description="Commpany jkjkfjkdbasjdjckdjkdjed huwhdiuehduehdu",
            owner=self.user
        )

        self.job = JobListing.objects.create(
            company=self.company,
            job_title="oracle developer",
            job_description="kwdwkdlkdl",
            job_location="Kollam",
            salary="60000"
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse('job-list')

    def test_update_job_success(self):
        data = {
            # "job_title": "developer",
            # "job_description": "kwdwkdlkdl",
            "job_location": "kochi",
            # "salary": "24000"
        }
        self.url = self.url+str(self.job.id)+'/'
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class JobViewSetDeleteTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123',
            email='testuser@example.com',
            roles='employer'
        )

        self.candidate = User.objects.create_user(
            username='testcandidate',
            password='testpassword123',
            email='testcandidate@example.com',
            roles='candidate'
        )

        self.admin = User.objects.create_superuser(
            username='admin',
            password='adminpassword',
            email='admin@example.com'
        )

        self.company = Company.objects.create(
            company_name="Ola",
            company_location="Trissur",
            description="Commpany jkjkfjkdbasjdjckdjkdjed huwhdiuehduehdu",
            owner=self.user
        )

        self.job = JobListing.objects.create(
            company=self.company,
            job_title="oracle developer",
            job_description="kwdwkdlkdl",
            job_location="Kollam",
            salary="60000"
        )

        self.client.force_authenticate(user=self.user)
        self.url = reverse('job-list')
        self.url = self.url+str(self.job.id)+'/'

    def test_delete_job_success(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_candidate_cannot_delete(self):
        self.client.force_authenticate(user=self.candidate)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


