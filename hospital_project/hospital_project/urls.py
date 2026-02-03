"""
URL configuration for hospital_project project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('patients/', include('patients.urls')),
    path('doctors/', include('doctors.urls')),
    path('appointments/', include('appointments.urls')),
    path('analytics/', include('analytics.urls')),
    path('payments/', include('payments.urls')),
    path('diagnosis/', include('diagnosis.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
