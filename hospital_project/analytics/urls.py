from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.analytics_dashboard, name='analytics_dashboard'),
    path('doctors/', views.doctor_analytics, name='doctor_analytics'),
    path('patients/', views.patient_analytics, name='patient_analytics'),
    path('revenue/', views.revenue_analytics, name='revenue_analytics'),
    path('appointments/', views.appointment_analytics, name='appointment_analytics'),
]
