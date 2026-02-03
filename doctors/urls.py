from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.doctor_register, name='doctor_register'),
    path('login/', views.doctor_login, name='doctor_login'),
    path('dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('logout/', views.doctor_logout, name='doctor_logout'),
    path('profile/', views.doctor_profile, name='doctor_profile'),
    path('manage-availability/', views.manage_availability, name='manage_availability'),
    path('approve/<int:appointment_id>/', views.approve_appointment, name='approve_appointment'),
    path('reject/<int:appointment_id>/', views.reject_appointment, name='reject_appointment'),
    path('add-notes/<int:appointment_id>/', views.add_doctor_notes, name='add_doctor_notes'),
]
