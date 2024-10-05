from django.conf import settings
from django.core.mail import send_mail
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, filters, request
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.company.models import Company
from apps.jobs.models import JobListing, JobApplication
from apps.jobs.serializers import JobSerializer, JobApplicationSerializer
from apps.permissions import IsEmployer, IsCandidate


class JobViewSet(viewsets.ModelViewSet):
    queryset = JobListing.objects.all()
    serializer_class = JobSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = [
        "job_title",
        "job_description",
        "company__company_name",
        "job_location",
    ]
    filterset_fields = ["salary", "job_location", "is_active"]

    permission_classes = [IsAuthenticated, IsEmployer | IsCandidate]

    def create(self, request):
        """
        - Creates a new job for the employer.
        - `request`: The HTTP request containing job details (job_title, job_description, job_location, salary).
        - **Returns**:
            - 201 Created if the job is successfully created.
            - 404 Not Found if the user does not have an associated company.
        """
        if request.user.roles != "employer":
            return Response(
                {"message": "You must be an employer to access this resource."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = JobSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        try:
            owner_company = Company.objects.get(owner=user)
        except Company.DoesNotExist:
            return Response(
                {"message": "User does not have an associated company"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer.save(company=owner_company)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        """
          - Filters job listings based on the user's role.
        - **Role-based access**:
            - Employers see only their job listings.
            - Candidates see only active job listings.
        - **Returns**:
            - Queryset of jobs based on role-specific filtering.
        """

        jobs = JobListing.objects.all()
        if self.request.user.roles == "employer":

            owner_company = get_object_or_404(Company, owner=self.request.user)
            jobs = jobs.filter(company=owner_company)
        elif self.request.user.roles == "candidate":
            jobs = jobs.filter(is_active=True)
        return jobs

    def partial_update(self, request, pk=None):
        """
          - Partially updates a job listing.
        - **Permissions**: Only employers who own the job listing can update it.
        - **Arguments**:
            - `request`: The HTTP request containing the fields to update.
            - `pk`: The primary key of the job listing.
        - **Returns**:
            - 200 OK if the job is successfully updated.
            - 404 Not Found if the job listing or company is not found.
        """
        if request.user.roles != "employer":
            return Response(
                {"message": "You must be an employer to access this resource."},
                status=status.HTTP_403_FORBIDDEN,
            )
        job_listing = get_object_or_404(JobListing, pk=pk, company__owner=request.user)
        serializer = JobSerializer(job_listing, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        """
           - Deletes a job listing.
        - **Permissions**:
            - Only employers who own the job listing or admins can delete it.
        - **Arguments**:
            - `request`: The HTTP request.
            - `pk`: The primary key of the job listing.
        - **Returns**:
            - 204 No Content if the job is successfully deleted.
            - 403 Forbidden if the user does not have permission to delete the job listing.
        """
        if request.user.roles != "employer" or (
            request.user.roles == "candidate" and not request.user.is_staff
        ):
            return Response(
                {
                    "message": "You must be an employer or admin to access this resource."
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        if request.user.roles == "employer":
            job_listing = get_object_or_404(
                JobListing, pk=pk, company__owner=request.user
            )
            job_listing.delete()
        elif request.user.is_staff:
            job_listing = get_object_or_404(JobListing, pk=pk)
            job_listing.delete()
        return Response(
            {"message": "Job deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )


class JobApplicationViewSet(viewsets.ModelViewSet):
    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationSerializer
    permission_classes = [IsAuthenticated, IsCandidate]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = [
        "status",
    ]

    def create(self, request, *args, **kwargs):
        """
        Candidate can apply for the job.
        - `request`: The HTTP request containing job application data.
        **Returns**:
        - Success: 201 Created with the serialized job application.
        - Failure: 400 Bad Request if data is invalid, or 403 if user is not a candidate.
        - Sends a confirmation email to the candidate after successful job application.
        """
        # if request.user.roles != 'candidate':
        #     return Response({'message': 'Only candidates can apply for jobs.'}, status=status.HTTP_403_FORBIDDEN)

        job_id = request.data.get("job")
        if not job_id:
            return Response(
                {"message": "Job ID is required."}, status=status.HTTP_400_BAD_REQUEST
            )
        job = get_object_or_404(JobListing, pk=job_id)

        if JobApplication.objects.filter(job=job, candidate=request.user).exists():
            return Response(
                {"message": "You have already applied to this job."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(candidate=request.user, job=job)
        subject = "Your application was send successfully."
        message = (
            f"Dear {request.user.username},\n\n Applied for the job {job.job_title} "
        )
        from_email = job.company.owner.email
        recipient_list = [request.user.email]
        send_mail(subject, message, from_email, recipient_list)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        """
        Retrieves job applications made by the currently authenticated candidate.
        """
        applications = JobApplication.objects.filter(candidate=self.request.user)
        return applications

    def partial_update(self, request, pk=None):
        """
        Updates the job application partially,only candidates are allowed to update the job application.
        - `request`: The HTTP request containing partial update data.
        - `pk`: The primary key of the job listing.
        - **Returns**:
            - 200 OK with the updated job application data.
            - 404 Not Found if the job or application does not exist.
        """
        job_obj = get_object_or_404(JobListing, pk=pk)
        job_application_obj = get_object_or_404(
            JobApplication, job=job_obj, candidate=self.request.user
        )
        serializer = JobApplicationSerializer(
            job_application_obj, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        """
        Delete the job application, only candidates are allowed to delete the job application.
        -`pk`: The primary key of the job listing.
        - **Returns**:
            - 200 OK with the updated job application data.
            - 404 Not Found if the job or application does not exist.
        """
        job_obj = get_object_or_404(JobListing, pk=pk)
        job_application_obj = get_object_or_404(
            JobApplication, job=job_obj, candidate=self.request.user
        )
        job_application_obj.delete()
        return Response(
            {"message": "Job deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )


class EmployerJobApplicationViewSet(viewsets.ModelViewSet):
    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationSerializer
    permission_classes = [IsAuthenticated, IsEmployer]

    @action(detail=True, methods=["patch"], url_path="change-status")
    def change_status(self, request, pk=None):
        """
        Allows employers to change the status of a job application.
            - `request`: The HTTP request containing the new status (`pending`, `accepted`, `rejected`).
            - `pk`: The primary key of the job application.
        - **Returns**:
            - 200 OK if the status is updated successfully.
            - 400 Bad Request if the status is invalid.
            - 404 Not Found if the job application does not exist.
        - Sends an email to the candidate notifying them of the status change.
        """
        job_application = get_object_or_404(JobApplication, pk=pk)
        new_status = request.data.get("status")
        if new_status not in ["pending", "accepted", "rejected"]:
            return Response(
                {"message": "Invalid entry"}, status=status.HTTP_400_BAD_REQUEST
            )
        job_application.status = new_status
        job_application.save()
        subject = "Status Changed"
        message = (
            f"Dear {request.user.username},\n\n Your job status changed for the {job_application.job.job_title}, "
            f"at{job_application.job.company.company_name} "
        )
        from_email = request.user.email
        recipient_list = [job_application.candidate.email]
        send_mail(subject, message, from_email, recipient_list)
        return Response(
            {
                "message": "Status Updated Successfully",
                "status": job_application.status,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["get"], url_path="applicants")
    def list_applications(self, request, pk=None):
        """
        Lists all applications for a specific job listing.
        - **Arguments**:
            - `request`: The HTTP request.
            - `pk`: The primary key of the job listing.
        - **Returns**:
            - 200 OK with the serialized list of applications.
            - 403 Forbidden if the employer does not own the job listing.
            - 404 Not Found if the job listing does not exist.
        """
        job = get_object_or_404(JobListing, pk=pk)
        if job.company.owner != request.user:
            return Response(
                {
                    "detail": "You do not have permission to view applications for this job."
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        applications = JobApplication.objects.filter(job=job)
        serializer = JobApplicationSerializer(applications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
