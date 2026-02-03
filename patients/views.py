from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Avg
from datetime import datetime, timedelta
from .models import Patient, PatientMedicalHistory
from .forms import PatientRegistrationForm, PatientLoginForm
from appointments.models import Appointment, AppointmentRating, WaitingList, DoctorNote
from doctors.models import Doctor, DoctorSpecialization, DoctorAvailability


def patient_register(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            # Create user
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name']
            )
            
            # Create patient profile
            Patient.objects.create(
                user=user,
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'],
                date_of_birth=form.cleaned_data['date_of_birth']
            )
            
            return redirect('patient_login')
    else:
        form = PatientRegistrationForm()
    
    return render(request, 'patients/register.html', {'form': form})


def patient_login(request):
    if request.method == 'POST':
        form = PatientLoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user is not None:
                # Check if user has a patient profile
                try:
                    Patient.objects.get(user=user)
                    login(request, user)
                    return redirect('patient_dashboard')
                except Patient.DoesNotExist:
                    form.add_error(None, "This account is not a patient account")
            else:
                form.add_error(None, "Invalid username or password")
    else:
        form = PatientLoginForm()
    
    return render(request, 'patients/login.html', {'form': form})


@login_required(login_url='patient_login')
def patient_dashboard(request):
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        logout(request)
        return redirect('patient_login')
    
    appointments = Appointment.objects.filter(patient=patient).order_by('-appointment_date')
    pending_appointments = appointments.filter(status='pending')
    approved_appointments = appointments.filter(status='approved')
    completed = appointments.filter(status='completed').count()
    
    # Medical history summary
    medical_history = PatientMedicalHistory.objects.filter(patient=patient).order_by('-created_at')[:5]
    
    # Diagnosis history - import DiagnosisRecord
    from diagnosis.models import DiagnosisRecord
    diagnosis_records = DiagnosisRecord.objects.filter(
        patient=patient
    ).prefetch_related('symptoms', 'predicted_specialization').order_by('-created_at')
    
    # Bills
    from payments.models import Bill
    bills = Bill.objects.filter(patient=patient).order_by('-bill_date')
    unpaid_bills = bills.filter(payment_status__in=['unpaid', 'partial', 'overdue'])
    total_due = sum(bill.remaining_amount for bill in unpaid_bills)
    total_bills_amount = sum(bill.total_amount for bill in bills)
    
    # Waiting list status
    waiting_list = WaitingList.objects.filter(patient=patient, status='waiting')
    
    return render(request, 'patients/dashboard.html', {
        'patient': patient,
        'appointments': appointments,
        'pending_appointments': pending_appointments,
        'approved_appointments': approved_appointments,
        'completed': completed,
        'medical_history': medical_history,
        'diagnosis_records': diagnosis_records,
        'bills': bills,
        'total_bills_amount': float(total_bills_amount),
        'total_due': float(total_due),
        'waiting_list': waiting_list,
    })


@login_required(login_url='patient_login')
def patient_profile(request):
    """View and edit patient profile including medical info"""
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        logout(request)
        return redirect('patient_login')
    
    if request.method == 'POST':
        patient.phone = request.POST.get('phone', patient.phone)
        patient.address = request.POST.get('address', patient.address)
        patient.blood_type = request.POST.get('blood_type', patient.blood_type)
        patient.emergency_contact = request.POST.get('emergency_contact', patient.emergency_contact)
        patient.insurance_provider = request.POST.get('insurance_provider', patient.insurance_provider)
        patient.insurance_id = request.POST.get('insurance_id', patient.insurance_id)
        patient.insurance_status = request.POST.get('insurance_status', patient.insurance_status)
        patient.save()
        return redirect('patient_profile')
    
    medical_history = PatientMedicalHistory.objects.filter(patient=patient).order_by('-created_at')
    
    return render(request, 'patients/profile.html', {
        'patient': patient,
        'medical_history': medical_history,
    })


@login_required(login_url='patient_login')
def search_doctors(request):
    """Advanced doctor search with filters"""
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        logout(request)
        return redirect('patient_login')
    
    specialization = request.GET.get('specialization')
    min_rating = request.GET.get('min_rating', 0)
    max_fee = request.GET.get('max_fee', 10000)
    available_only = request.GET.get('available_only') == 'on'
    
    doctors = Doctor.objects.all()
    
    if specialization:
        doctors = doctors.filter(specialization__name__icontains=specialization)
    
    doctors = doctors.filter(
        rating__gte=min_rating,
        consultation_fee__lte=max_fee
    )
    
    if available_only:
        doctors = doctors.filter(availability_status='available')
    
    doctors = doctors.order_by('-rating', 'consultation_fee')
    
    specializations = DoctorSpecialization.objects.all()
    
    return render(request, 'patients/search_doctors.html', {
        'doctors': doctors,
        'specializations': specializations,
        'patient': patient,
    })


@login_required(login_url='patient_login')
def view_doctor_profile(request, doctor_id):
    """View detailed doctor profile with reviews"""
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        logout(request)
        return redirect('patient_login')
    
    doctor = get_object_or_404(Doctor, id=doctor_id)
    availability = DoctorAvailability.objects.filter(doctor=doctor).order_by('day_of_week')
    reviews = AppointmentRating.objects.filter(doctor=doctor).order_by('-created_at')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    return render(request, 'patients/doctor_profile.html', {
        'doctor': doctor,
        'patient': patient,
        'availability': availability,
        'reviews': reviews,
        'avg_rating': avg_rating,
    })


def patient_logout(request):
    logout(request)
    return redirect('patient_login')


@login_required(login_url='patient_login')
def book_appointment(request):
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        logout(request)
        return redirect('patient_login')
    
    # Get pre-filled data from query parameters (from diagnosis)
    pre_selected_doctor = request.GET.get('doctor')
    pre_filled_condition = request.GET.get('condition')
    pre_filled_symptoms = request.GET.get('symptoms')
    
    if request.method == 'POST':
        from appointments.forms import AppointmentBookingForm
        form = AppointmentBookingForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = patient
            # Store pre-filled symptoms/condition if available
            if pre_filled_condition or pre_filled_symptoms:
                appointment.reason = f"{pre_filled_condition or 'Check-up'}\nSymptoms: {pre_filled_symptoms or 'N/A'}"
            appointment.save()
            return redirect('patient_dashboard')
    else:
        from appointments.forms import AppointmentBookingForm
        form = AppointmentBookingForm()
        # Pre-select doctor if provided from diagnosis
        if pre_selected_doctor:
            form.fields['doctor'].initial = pre_selected_doctor
    
    # Get all doctors for display
    doctors = Doctor.objects.all()
    
    context = {
        'form': form,
        'doctors': doctors,
        'patient': patient,
        'pre_filled_condition': pre_filled_condition,
        'pre_filled_symptoms': pre_filled_symptoms,
        'pre_selected_doctor': pre_selected_doctor,
    }
    
    return render(request, 'patients/book_appointment.html', context)


@login_required(login_url='patient_login')
def reschedule_appointment(request, appointment_id):
    """Reschedule a pending appointment"""
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        logout(request)
        return redirect('patient_login')
    
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=patient, status='pending')
    
    if request.method == 'POST':
        new_date = request.POST.get('appointment_date')
        new_time = request.POST.get('appointment_time')
        
        appointment.appointment_date = new_date
        appointment.appointment_time = new_time
        appointment.save()
        
        return redirect('patient_dashboard')
    
    return render(request, 'patients/reschedule_appointment.html', {
        'appointment': appointment,
        'patient': patient,
    })


@login_required(login_url='patient_login')
def cancel_appointment(request, appointment_id):
    """Cancel appointment with auto-reschedule suggestions"""
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        logout(request)
        return redirect('patient_login')
    
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=patient)
    
    if request.method == 'POST':
        appointment.status = 'cancelled'
        appointment.save()
        
        # Suggest alternative slots
        return redirect('suggest_appointments', doctor_id=appointment.doctor.id)
    
    return render(request, 'patients/cancel_appointment.html', {
        'appointment': appointment,
        'patient': patient,
    })


@login_required(login_url='patient_login')
def suggest_appointments(request, doctor_id):
    """Suggest alternative appointment slots when canceling"""
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        logout(request)
        return redirect('patient_login')
    
    doctor = get_object_or_404(Doctor, id=doctor_id)
    availability = DoctorAvailability.objects.filter(doctor=doctor).order_by('day_of_week')
    
    return render(request, 'patients/suggest_appointments.html', {
        'doctor': doctor,
        'patient': patient,
        'availability': availability,
    })


@login_required(login_url='patient_login')
def rate_appointment(request, appointment_id):
    """Rate and review completed appointment"""
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        logout(request)
        return redirect('patient_login')
    
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=patient, status='completed')
    
    if request.method == 'POST':
        rating = int(request.POST.get('rating'))
        review_text = request.POST.get('review_text', '')
        is_anonymous = request.POST.get('is_anonymous') == 'on'
        
        # Create or update rating
        app_rating, created = AppointmentRating.objects.update_or_create(
            appointment=appointment,
            patient=patient,
            defaults={
                'doctor': appointment.doctor,
                'rating': rating,
                'review_text': review_text,
                'is_anonymous': is_anonymous
            }
        )
        
        # Update doctor's rating
        appointment.doctor.update_rating()
        
        return redirect('patient_dashboard')
    
    try:
        existing_rating = AppointmentRating.objects.get(appointment=appointment, patient=patient)
    except AppointmentRating.DoesNotExist:
        existing_rating = None
    
    return render(request, 'patients/rate_appointment.html', {
        'appointment': appointment,
        'patient': patient,
        'existing_rating': existing_rating,
    })


@login_required(login_url='patient_login')
def medical_history(request):
    """View complete medical history"""
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        logout(request)
        return redirect('patient_login')
    
    history = PatientMedicalHistory.objects.filter(patient=patient).order_by('-created_at')
    
    return render(request, 'patients/medical_history.html', {
        'patient': patient,
        'history': history,
    })


@login_required(login_url='patient_login')
def view_prescription(request, note_id):
    """View doctor's prescription and clinical notes"""
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        logout(request)
        return redirect('patient_login')
    
    note = get_object_or_404(DoctorNote, appointment__patient=patient, id=note_id)
    
    return render(request, 'patients/view_prescription.html', {
        'note': note,
        'patient': patient,
    })


@login_required(login_url='patient_login')
def waiting_list(request):
    """View and manage waiting list entries"""
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        logout(request)
        return redirect('patient_login')
    
    entries = WaitingList.objects.filter(patient=patient).order_by('position_in_queue')
    
    return render(request, 'patients/waiting_list.html', {
        'patient': patient,
        'entries': entries,
    })
