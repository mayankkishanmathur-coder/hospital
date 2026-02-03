from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.patient_register, name='patient_register'),
    path('login/', views.patient_login, name='patient_login'),
    path('dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('logout/', views.patient_logout, name='patient_logout'),
    path('profile/', views.patient_profile, name='patient_profile'),
    path('book-appointment/', views.book_appointment, name='book_appointment'),
    path('search-doctors/', views.search_doctors, name='search_doctors'),
    path('doctor/<int:doctor_id>/', views.view_doctor_profile, name='view_doctor_profile'),
    path('reschedule/<int:appointment_id>/', views.reschedule_appointment, name='reschedule_appointment'),
    path('cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('suggest-appointments/<int:doctor_id>/', views.suggest_appointments, name='suggest_appointments'),
    path('rate/<int:appointment_id>/', views.rate_appointment, name='rate_appointment'),
    path('medical-history/', views.medical_history, name='medical_history'),
    path('prescription/<int:note_id>/', views.view_prescription, name='view_prescription'),
    path('waiting-list/', views.waiting_list, name='waiting_list'),
]
