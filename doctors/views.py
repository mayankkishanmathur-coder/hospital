from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Doctor, DoctorSpecialization, DoctorAvailability, Department
from .forms import DoctorRegistrationForm, DoctorLoginForm, DoctorAvailabilityForm
from appointments.models import Appointment, DoctorNote, AppointmentRating, WaitingList
from patients.models import Patient, PatientMedicalHistory


def doctor_register(request):
    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST)
        if form.is_valid():
            # Create user
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name']
            )
            
            # Create doctor profile
            Doctor.objects.create(
                user=user,
                specialization=form.cleaned_data['specialization'],
                phone=form.cleaned_data['phone'],
                license_number=form.cleaned_data['license_number'],
                experience_years=form.cleaned_data['experience_years'],
                clinic_address=form.cleaned_data['clinic_address'],
                consultation_fee=form.cleaned_data['consultation_fee']
            )
            
            return redirect('doctor_login')
    else:
        form = DoctorRegistrationForm()
    
    return render(request, 'doctors/register.html', {'form': form})


def doctor_login(request):
    if request.method == 'POST':
        form = DoctorLoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user is not None:
                # Check if user has a doctor profile
                try:
                    Doctor.objects.get(user=user)
                    login(request, user)
                    return redirect('doctor_dashboard')
                except Doctor.DoesNotExist:
                    form.add_error(None, "This account is not a doctor account")
            else:
                form.add_error(None, "Invalid username or password")
    else:
        form = DoctorLoginForm()
    
    return render(request, 'doctors/login.html', {'form': form})


@login_required(login_url='doctor_login')
def doctor_dashboard(request):
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        logout(request)
        return redirect('doctor_login')
    
    appointments = Appointment.objects.filter(doctor=doctor)
    pending_appointments = appointments.filter(status='pending')
    approved_appointments = appointments.filter(status='approved')
    rejected_appointments = appointments.filter(status='rejected')
    completed_appointments = appointments.filter(status='completed')
    
    # Analytics
    total_patients = appointments.values('patient').distinct().count()
    avg_rating = doctor.rating
    total_reviews = doctor.total_ratings
    waiting_list_count = WaitingList.objects.filter(doctor=doctor, status='waiting').count()
    
    return render(request, 'doctors/dashboard.html', {
        'doctor': doctor,
        'appointments': appointments,
        'pending_appointments': pending_appointments,
        'approved_appointments': approved_appointments,
        'rejected_appointments': rejected_appointments,
        'completed_appointments': completed_appointments,
        'total_patients': total_patients,
        'avg_rating': avg_rating,
        'total_reviews': total_reviews,
        'waiting_list_count': waiting_list_count,
    })


@login_required(login_url='doctor_login')
def doctor_profile(request):
    """View and edit doctor profile"""
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        logout(request)
        return redirect('doctor_login')
    
    if request.method == 'POST':
        doctor.bio = request.POST.get('bio', doctor.bio)
        doctor.qualifications = request.POST.get('qualifications', doctor.qualifications)
        doctor.phone = request.POST.get('phone', doctor.phone)
        doctor.clinic_address = request.POST.get('clinic_address', doctor.clinic_address)
        doctor.consultation_fee = request.POST.get('consultation_fee', doctor.consultation_fee)
        if request.FILES.get('profile_image'):
            doctor.profile_image = request.FILES['profile_image']
        doctor.save()
        return redirect('doctor_profile')
    
    availability = DoctorAvailability.objects.filter(doctor=doctor).order_by('day_of_week')
    reviews = AppointmentRating.objects.filter(doctor=doctor)
    
    return render(request, 'doctors/profile.html', {
        'doctor': doctor,
        'availability': availability,
        'reviews': reviews,
    })


@login_required(login_url='doctor_login')
def manage_availability(request):
    """Manage working hours and availability"""
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        logout(request)
        return redirect('doctor_login')
    
    if request.method == 'POST':
        form = DoctorAvailabilityForm(request.POST, instance=doctor)
        if form.is_valid():
            form.save()
            return redirect('manage_availability')
    else:
        form = DoctorAvailabilityForm(instance=doctor)
    
    availability = DoctorAvailability.objects.filter(doctor=doctor).order_by('day_of_week')
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    return render(request, 'doctors/manage_availability.html', {
        'doctor': doctor,
        'form': form,
        'availability': availability,
        'days': days
    })


@login_required(login_url='doctor_login')
def approve_appointment(request, appointment_id):
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        return redirect('doctor_login')
    
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=doctor)
    
    if request.method == 'POST':
        appointment.status = 'approved'
        appointment.save()
        return redirect('doctor_dashboard')
    
    return render(request, 'doctors/approve_appointment.html', {
        'appointment': appointment
    })


@login_required(login_url='doctor_login')
def add_doctor_notes(request, appointment_id):
    """Add medical notes and prescription after appointment"""
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        return redirect('doctor_login')
    
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=doctor)
    
    if request.method == 'POST':
        prescription = request.POST.get('prescription')
        clinical_notes = request.POST.get('clinical_notes')
        follow_up_required = request.POST.get('follow_up_required') == 'on'
        follow_up_days = request.POST.get('follow_up_days', 7)
        
        # Create or update doctor note
        note, created = DoctorNote.objects.update_or_create(
            appointment=appointment,
            defaults={
                'doctor': doctor,
                'prescription': prescription,
                'clinical_notes': clinical_notes,
                'follow_up_required': follow_up_required,
                'follow_up_days': follow_up_days
            }
        )
        
        # Create medical history record
        PatientMedicalHistory.objects.create(
            patient=appointment.patient,
            appointment=appointment,
            diagnosis=request.POST.get('diagnosis', ''),
            medications=prescription,
            allergies=request.POST.get('allergies', ''),
            notes=clinical_notes
        )
        
        # If follow-up needed, add to waiting list or auto-create
        if follow_up_required:
            follow_up_date = appointment.appointment_date + timedelta(days=int(follow_up_days))
            WaitingList.objects.create(
                patient=appointment.patient,
                doctor=doctor,
                preferred_date_from=follow_up_date,
                preferred_date_to=follow_up_date + timedelta(days=7),
                reason=f"Follow-up: {clinical_notes[:100]}"
            )
        
        appointment.status = 'completed'
        appointment.save()
        
        return redirect('doctor_dashboard')
    
    try:
        doctor_note = DoctorNote.objects.get(appointment=appointment)
    except DoctorNote.DoesNotExist:
        doctor_note = None
    
    return render(request, 'doctors/add_doctor_notes.html', {
        'appointment': appointment,
        'doctor_note': doctor_note
    })


@login_required(login_url='doctor_login')
def reject_appointment(request, appointment_id):
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        return redirect('doctor_login')
    
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=doctor)
    
    if request.method == 'POST':
        rejection_reason = request.POST.get('rejection_reason')
        appointment.status = 'rejected'
        appointment.rejection_reason = rejection_reason
        appointment.save()
        
        # Try to reassign to another doctor
        reassign_appointment(appointment)
        
        return redirect('doctor_dashboard')
    
    return render(request, 'doctors/reject_appointment.html', {
        'appointment': appointment
    })


def reassign_appointment(appointment):
    """Reassign appointment to another available doctor with same specialization"""
    available_doctors = Doctor.objects.filter(
        specialization=appointment.doctor.specialization,
        availability_status='available'
    ).exclude(id=appointment.doctor.id)
    
    if available_doctors.exists():
        new_doctor = available_doctors.first()
        appointment.doctor = new_doctor
        appointment.status = 'pending'
        appointment.save()


def doctor_logout(request):
    logout(request)
    return redirect('doctor_login')
