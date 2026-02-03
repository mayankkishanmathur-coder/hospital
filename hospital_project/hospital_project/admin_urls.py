from django.urls import path
from . import admin_views

urlpatterns = [
    path('dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('users/', admin_views.manage_users, name='manage_users'),
    path('doctors/', admin_views.manage_doctors, name='manage_doctors'),
    path('patients/', admin_views.manage_patients, name='manage_patients'),
    path('appointments/', admin_views.manage_appointments, name='manage_appointments'),
    path('appointments/<int:appointment_id>/approve/', admin_views.approve_appointment, name='admin_approve_appointment'),
    path('appointments/<int:appointment_id>/reject/', admin_views.reject_appointment, name='admin_reject_appointment'),
    path('statistics/', admin_views.statistics, name='statistics'),
]
