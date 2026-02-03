from django.urls import path
from . import views

urlpatterns = [
    path('detail/<int:appointment_id>/', views.appointment_detail, name='appointment_detail'),
    path('cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
]
