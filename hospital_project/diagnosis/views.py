from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .forms import DiagnosisForm
from .models import Symptom, DiagnosisRecord
from .ml_model import get_diagnosis_model
from .notifications import send_diagnosis_notification
from patients.models import Patient
from doctors.models import Doctor, DoctorSpecialization
from django.db.models import Q


@login_required(login_url='patient_login')
@require_http_methods(["GET", "POST"])
def diagnosis_index(request):
    """Self-diagnosis portal - symptom selection and submission"""
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        messages.error(request, 'Patient profile not found.')
        return redirect('patient_login')
    
    if request.method == 'POST':
        form = DiagnosisForm(request.POST)
        if form.is_valid():
            selected_symptoms = form.get_selected_symptoms()
            other_symptoms_keywords = form.get_other_symptoms_as_keywords()
            
            # Combine selected symptoms with extracted keywords
            all_symptoms = list(set(selected_symptoms + other_symptoms_keywords))
            
            severity_info = form.get_symptom_severity_info()
            
            if not all_symptoms:
                messages.warning(request, 'Please select at least one symptom or describe your symptoms in the text field.')
                return render(request, 'diagnosis/index.html', {'form': form})
            
            # Check for urgent symptoms
            if severity_info['urgent'] > 0:
                messages.warning(
                    request, 
                    f'⚠️ You have selected {severity_info["urgent"]} urgent symptom(s). '
                    'Please seek immediate medical attention if experiencing severe symptoms.'
                )
            
            # Log extracted keywords if any
            if other_symptoms_keywords:
                messages.info(
                    request,
                    f'✓ Extracted keywords from your description: {", ".join(other_symptoms_keywords)}'
                )
            
            # Get ML model and make prediction
            model = get_diagnosis_model()
            predicted_condition, predicted_specialization, confidence = model.predict_condition(all_symptoms)
            
            if not predicted_condition:
                messages.error(request, 'Unable to make prediction. Please try again.')
                return render(request, 'diagnosis/index.html', {'form': form})
            
            # Store diagnosis record
            diagnosis_record = DiagnosisRecord.objects.create(
                patient=patient,
                predicted_condition=predicted_condition,
                predicted_specialization=DoctorSpecialization.objects.filter(name=predicted_specialization).first(),
                confidence_score=confidence
            )
            
            # Add all symptoms (selected + extracted) to record
            symptom_ids = Symptom.objects.filter(name__in=all_symptoms).values_list('id', flat=True)
            diagnosis_record.symptoms.set(symptom_ids)
            diagnosis_record.save()  # Trigger auto-calculation of confidence_level and has_urgent_symptoms
            
            # Send email notification
            send_diagnosis_notification(diagnosis_record)
            
            # Add confidence threshold warning if applicable
            if confidence < 0.6:
                messages.info(
                    request,
                    '⚠️ Low confidence prediction. Consult a doctor for accurate diagnosis.'
                )
            
            # Redirect to results page
            return redirect('diagnosis_results', record_id=diagnosis_record.id)
    else:
        form = DiagnosisForm()
    
    # Get symptoms grouped by category
    symptoms = Symptom.objects.filter(is_active=True).order_by('category', 'name')
    categories = {}
    
    for symptom in symptoms:
        category = symptom.category or 'Other'
        if category not in categories:
            categories[category] = []
        categories[category].append(symptom)
    
    return render(request, 'diagnosis/index.html', {
        'form': form,
        'categories': categories,
        'symptoms': symptoms
    })


@login_required(login_url='patient_login')
def diagnosis_results(request, record_id):
    """Display diagnosis results and recommended doctors"""
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        messages.error(request, 'Patient profile not found.')
        return redirect('patient_login')
    
    # Get diagnosis record
    diagnosis_record = get_object_or_404(DiagnosisRecord, id=record_id, patient=patient)
    
    # Get recommended doctors
    recommended_doctors = []
    if diagnosis_record.predicted_specialization:
        recommended_doctors = Doctor.objects.filter(
            specialization=diagnosis_record.predicted_specialization,
            availability_status='available'
        ).select_related('user', 'specialization')[:5]
    
    # Prepare context with warnings
    context = {
        'diagnosis_record': diagnosis_record,
        'predicted_condition': diagnosis_record.predicted_condition,
        'predicted_specialization': diagnosis_record.predicted_specialization,
        'confidence_score': round(diagnosis_record.confidence_score * 100, 1),
        'confidence_level': diagnosis_record.get_confidence_level_display(),
        'has_urgent_symptoms': diagnosis_record.has_urgent_symptoms,
        'symptoms': diagnosis_record.symptoms.all(),
        'recommended_doctors': recommended_doctors,
        'show_confidence_warning': diagnosis_record.confidence_score < 0.6,
        'show_urgent_warning': diagnosis_record.has_urgent_symptoms,
    }
    
    return render(request, 'diagnosis/results.html', context)


@login_required(login_url='patient_login')
def book_from_diagnosis(request, record_id, doctor_id):
    """Redirect to appointment booking with pre-filled diagnosis data"""
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        messages.error(request, 'Patient profile not found.')
        return redirect('patient_login')
    
    # Get diagnosis record
    diagnosis_record = get_object_or_404(DiagnosisRecord, id=record_id, patient=patient)
    
    # Get doctor
    doctor = get_object_or_404(Doctor, id=doctor_id)
    
    # Update the diagnosis record with booked doctor
    diagnosis_record.booked_doctor = doctor
    diagnosis_record.save()
    
    # Build query parameters with pre-filled data
    from django.urls import reverse
    condition = diagnosis_record.predicted_condition
    symptoms_text = ', '.join([s.name for s in diagnosis_record.symptoms.all()])
    
    # Redirect to booking page with parameters
    booking_url = reverse('book_appointment') + f'?doctor={doctor.id}&condition={condition}&symptoms={symptoms_text}'
    return redirect(booking_url)


@login_required(login_url='patient_login')
def diagnosis_history(request):
    """View diagnosis history for current patient"""
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        messages.error(request, 'Patient profile not found.')
        return redirect('patient_login')
    
    # Get all diagnosis records for patient
    diagnosis_records = DiagnosisRecord.objects.filter(
        patient=patient
    ).prefetch_related('symptoms', 'predicted_specialization', 'booked_doctor').order_by('-created_at')
    
    total_diagnoses = diagnosis_records.count()
    booked_count = diagnosis_records.filter(booked_doctor__isnull=False).count()
    
    context = {
        'diagnosis_records': diagnosis_records,
        'total_diagnoses': total_diagnoses,
        'booked_count': booked_count,
        'pending_count': total_diagnoses - booked_count,
    }
    
    return render(request, 'diagnosis/history.html', context)


@login_required(login_url='patient_login')
@require_http_methods(["POST"])
def delete_diagnosis(request, record_id):
    """Delete a diagnosis record"""
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        messages.error(request, 'Patient profile not found.')
        return redirect('patient_login')
    
    # Get the diagnosis record and verify it belongs to the current patient
    diagnosis_record = get_object_or_404(DiagnosisRecord, id=record_id, patient=patient)
    
    diagnosis_record.delete()
    messages.success(request, 'Diagnosis record has been deleted successfully.')
    
    # Redirect back to dashboard or referrer
    next_url = request.GET.get('next', 'patient_dashboard')
    return redirect(next_url)
