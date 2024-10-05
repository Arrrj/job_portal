from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.jobs.views import JobViewSet, JobApplicationViewSet, EmployerJobApplicationViewSet

router = DefaultRouter()
router.register(r'jobs', JobViewSet, basename='job')
router.register(r'applications', JobApplicationViewSet, basename='applications')
router.register(r'employer', EmployerJobApplicationViewSet, basename='employer')

urlpatterns = [
    path('', include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)