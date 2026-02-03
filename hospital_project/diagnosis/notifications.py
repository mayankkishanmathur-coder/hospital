from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import DiagnosisRecord


def send_diagnosis_notification(diagnosis_record):
    """Send email notification when diagnosis is completed"""
    try:
        patient_email = diagnosis_record.patient.user.email
        patient_name = diagnosis_record.patient.user.get_full_name()
        
        if not patient_email:
            return False
        
        # Prepare email context
        context = {
            'patient_name': patient_name,
            'condition': diagnosis_record.predicted_condition,
            'specialization': diagnosis_record.predicted_specialization,
            'confidence': round(diagnosis_record.confidence_score * 100, 1),
            'symptoms': diagnosis_record.symptoms.all(),
            'has_urgent': diagnosis_record.has_urgent_symptoms,
            'record_id': diagnosis_record.id,
        }
        
        # Render email template
        email_body = render_to_string('diagnosis/email_notification.html', context)
        
        # Send email
        send_mail(
            subject=f'Your Self-Diagnosis Results: {diagnosis_record.predicted_condition}',
            message=f"Check your diagnosis results for {diagnosis_record.predicted_condition}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[patient_email],
            html_message=email_body,
            fail_silently=False,
        )
        
        return True
    except Exception as e:
        print(f"Error sending diagnosis notification: {e}")
        return False


def send_booking_confirmation(diagnosis_record, appointment):
    """Send email confirmation when appointment is booked from diagnosis"""
    try:
        patient_email = diagnosis_record.patient.user.email
        patient_name = diagnosis_record.patient.user.get_full_name()
        
        if not patient_email:
            return False
        
        context = {
            'patient_name': patient_name,
            'doctor_name': appointment.doctor.user.get_full_name(),
            'doctor_specialization': appointment.doctor.specialization,
            'appointment_date': appointment.appointment_date,
            'appointment_time': appointment.appointment_time,
            'diagnosis_condition': diagnosis_record.predicted_condition,
        }
        
        email_body = render_to_string('diagnosis/email_booking_confirmation.html', context)
        
        send_mail(
            subject=f'Appointment Confirmed with {appointment.doctor.user.get_full_name()}',
            message=f"Your appointment is scheduled for {appointment.appointment_date}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[patient_email],
            html_message=email_body,
            fail_silently=False,
        )
        
        return True
    except Exception as e:
        print(f"Error sending booking confirmation: {e}")
        return False
