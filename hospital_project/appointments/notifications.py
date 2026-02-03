from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from datetime import timedelta
from django.utils import timezone


def send_appointment_confirmation(appointment):
    """Send appointment confirmation email to patient"""
    subject = 'Appointment Confirmation - MediBridge'
    html_message = f"""
    <h2>Appointment Confirmed</h2>
    <p>Dear {appointment.patient.user.first_name},</p>
    <p>Your appointment has been confirmed with Dr. {appointment.doctor.user.first_name} {appointment.doctor.user.last_name}.</p>
    <ul>
        <li><strong>Date:</strong> {appointment.appointment_date}</li>
        <li><strong>Time:</strong> {appointment.appointment_time}</li>
        <li><strong>Specialization:</strong> {appointment.doctor.specialization}</li>
        <li><strong>Clinic Address:</strong> {appointment.doctor.clinic_address}</li>
    </ul>
    <p>Please arrive 10 minutes before your appointment.</p>
    <p>Best regards,<br>MediBridge Team</p>
    """
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [appointment.patient.user.email],
        html_message=html_message,
        fail_silently=True,
    )


def send_appointment_reminder(appointment):
    """Send 24-hour reminder before appointment"""
    subject = 'Appointment Reminder - MediBridge'
    html_message = f"""
    <h2>Appointment Reminder</h2>
    <p>Hi {appointment.patient.user.first_name},</p>
    <p>Your appointment is tomorrow!</p>
    <p><strong>{appointment.appointment_date} at {appointment.appointment_time}</strong></p>
    <p>Doctor: Dr. {appointment.doctor.user.first_name} {appointment.doctor.user.last_name}</p>
    <p>If you need to reschedule, please contact us as soon as possible.</p>
    <p>Best regards,<br>MediBridge Team</p>
    """
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [appointment.patient.user.email],
        html_message=html_message,
        fail_silently=True,
    )


def send_appointment_approved(appointment):
    """Send approval notification to patient"""
    subject = 'Your Appointment Has Been Approved - MediBridge'
    html_message = f"""
    <h2>Appointment Approved</h2>
    <p>Dear {appointment.patient.user.first_name},</p>
    <p>Great news! Your appointment request has been approved by Dr. {appointment.doctor.user.first_name} {appointment.doctor.user.last_name}.</p>
    <p><strong>Appointment Details:</strong></p>
    <ul>
        <li>Date: {appointment.appointment_date}</li>
        <li>Time: {appointment.appointment_time}</li>
        <li>Doctor: Dr. {appointment.doctor.user.first_name} {appointment.doctor.user.last_name}</li>
        <li>Specialization: {appointment.doctor.specialization}</li>
    </ul>
    <p>Thank you for choosing MediBridge!</p>
    """
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [appointment.patient.user.email],
        html_message=html_message,
        fail_silently=True,
    )


def send_appointment_rejected(appointment):
    """Send rejection notification to patient"""
    subject = 'Appointment Status Update - MediBridge'
    html_message = f"""
    <h2>Appointment Update</h2>
    <p>Dear {appointment.patient.user.first_name},</p>
    <p>Your appointment with Dr. {appointment.doctor.user.first_name} {appointment.doctor.user.last_name} has been declined.</p>
    <p><strong>Reason:</strong> {appointment.rejection_reason or 'Doctor is unavailable at that time'}</p>
    <p>We've reassigned your request to another available doctor of the same specialization. You'll receive confirmation shortly.</p>
    <p>If you prefer a specific doctor, please try booking again.</p>
    <p>Best regards,<br>MediBridge Team</p>
    """
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [appointment.patient.user.email],
        html_message=html_message,
        fail_silently=True,
    )


def send_prescription_notification(doctor_note):
    """Notify patient when prescription is ready"""
    appointment = doctor_note.appointment
    subject = 'Your Prescription is Ready - MediBridge'
    html_message = f"""
    <h2>Prescription Ready</h2>
    <p>Hi {appointment.patient.user.first_name},</p>
    <p>Dr. {appointment.doctor.user.first_name} {appointment.doctor.user.last_name} has added your prescription and notes from the appointment.</p>
    <p><strong>Medications:</strong></p>
    <p>{doctor_note.prescription.replace(chr(10), '<br>')}</p>
    <p>Please log in to your MediBridge account to view full details and any follow-up instructions.</p>
    <p>Best regards,<br>MediBridge Team</p>
    """
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [appointment.patient.user.email],
        html_message=html_message,
        fail_silently=True,
    )


def send_followup_suggestion(doctor_note):
    """Send follow-up appointment suggestion"""
    appointment = doctor_note.appointment
    followup_date = doctor_note.get_follow_up_date()
    
    if followup_date:
        subject = 'Follow-Up Appointment Suggested - MediBridge'
        html_message = f"""
        <h2>Follow-Up Appointment Recommended</h2>
        <p>Hi {appointment.patient.user.first_name},</p>
        <p>Dr. {appointment.doctor.user.first_name} {appointment.doctor.user.last_name} recommends a follow-up appointment.</p>
        <p><strong>Suggested Date:</strong> {followup_date}</p>
        <p><strong>Reason:</strong> {doctor_note.clinical_notes[:100]}</p>
        <p>Please log in to book your follow-up appointment or contact our support team.</p>
        <p>Best regards,<br>MediBridge Team</p>
        """
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [appointment.patient.user.email],
            html_message=html_message,
            fail_silently=True,
        )


def send_waiting_list_notification(waiting_list_entry):
    """Notify patient when slot becomes available from waiting list"""
    subject = 'Available Appointment Slot - MediBridge'
    html_message = f"""
    <h2>Appointment Slot Available</h2>
    <p>Hi {waiting_list_entry.patient.user.first_name},</p>
    <p>Good news! A slot is now available with Dr. {waiting_list_entry.doctor.user.first_name} {waiting_list_entry.doctor.user.last_name}.</p>
    <p>Please log in to your account to book this appointment before it's taken by someone else.</p>
    <p>This offer is valid for 24 hours.</p>
    <p>Best regards,<br>MediBridge Team</p>
    """
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [waiting_list_entry.patient.user.email],
        html_message=html_message,
        fail_silently=True,
    )


def send_review_request(appointment):
    """Request patient to review the appointment"""
    if appointment.status != 'completed':
        return
    
    subject = 'Please Rate Your Appointment - MediBridge'
    html_message = f"""
    <h2>Your Feedback Matters</h2>
    <p>Hi {appointment.patient.user.first_name},</p>
    <p>We hope your appointment with Dr. {appointment.doctor.user.first_name} {appointment.doctor.user.last_name} went well!</p>
    <p>Please take a moment to rate your experience. Your feedback helps us improve our service.</p>
    <p><a href="http://yourdomain.com/patients/rate/{appointment.id}/">Rate This Appointment</a></p>
    <p>Thank you for choosing MediBridge!</p>
    """
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [appointment.patient.user.email],
        html_message=html_message,
        fail_silently=True,
    )
