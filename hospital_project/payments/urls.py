from django.urls import path
from . import views

urlpatterns = [
    path('pay/<int:appointment_id>/', views.payment_page, name='payment_page'),
    path('process/<int:appointment_id>/', views.process_payment, name='process_payment'),
    path('success/<int:appointment_id>/', views.payment_success, name='payment_success'),
    path('refund/<int:appointment_id>/', views.refund_appointment, name='refund_appointment'),
    path('bills/', views.bills_and_payments, name='bills_and_payments'),
]
