from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import Appointment
from patients.models import Patient
from doctors.models import Doctor


@login_required(login_url='patient_login')
def appointment_detail(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    return render(request, 'appointments/detail.html', {'appointment': appointment})


@login_required
@require_http_methods(["POST"])
def cancel_appointment(request, appointment_id):
    """Cancel an appointment - works for both patient and doctor"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Verify user is either the patient or doctor for this appointment
    is_patient = False
    is_doctor = False
    
    try:
        patient = Patient.objects.get(user=request.user)
        if appointment.patient == patient:
            is_patient = True
    except Patient.DoesNotExist:
        pass
    
    try:
        doctor = Doctor.objects.get(user=request.user)
        if appointment.doctor == doctor:
            is_doctor = True
    except Doctor.DoesNotExist:
        pass
    
    if not (is_patient or is_doctor):
        messages.error(request, 'You do not have permission to cancel this appointment.')
        return redirect('patient_login')
    
    # Only allow cancellation if appointment is pending or approved
    if appointment.status not in ['pending', 'approved']:
        messages.warning(request, f'Cannot cancel appointment with status: {appointment.get_status_display()}')
        next_url = request.GET.get('next', 'patient_dashboard')
        return redirect(next_url)
    
    appointment.status = 'cancelled'
    appointment.save()
    
    user_role = 'Patient' if is_patient else 'Doctor'
    messages.success(request, f'Appointment cancelled successfully by {user_role}.')
    
    # Redirect to appropriate dashboard
    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)
    
    if is_patient:
        return redirect('patient_dashboard')
    else:
        return redirect('doctor_dashboard')
