from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Avg, Sum
from django.utils import timezone
from datetime import timedelta
from patients.models import Patient
from doctors.models import Doctor, Department
from appointments.models import Appointment, AppointmentRating


def is_admin(user):
    """Check if user is admin"""
    return user.is_superuser or user.is_staff


@login_required
@user_passes_test(is_admin)
def analytics_dashboard(request):
    """Main analytics dashboard with KPIs and charts"""
    
    # Key metrics
    total_appointments = Appointment.objects.count()
    total_patients = Patient.objects.count()
    total_doctors = Doctor.objects.count()
    total_departments = Department.objects.count()
    
    # Appointment status breakdown
    pending = Appointment.objects.filter(status='pending').count()
    approved = Appointment.objects.filter(status='approved').count()
    completed = Appointment.objects.filter(status='completed').count()
    rejected = Appointment.objects.filter(status='rejected').count()
    cancelled = Appointment.objects.filter(status='cancelled').count()
    
    # Financial metrics
    total_revenue = sum([
        float(apt.doctor.consultation_fee) 
        for apt in Appointment.objects.filter(status='completed')
    ])
    
    # Ratings
    avg_rating = AppointmentRating.objects.aggregate(Avg('rating'))['rating__avg'] or 0
    total_reviews = AppointmentRating.objects.count()
    
    # Appointments last 7 days
    seven_days_ago = timezone.now() - timedelta(days=7)
    appointments_week = Appointment.objects.filter(created_at__gte=seven_days_ago).count()
    
    # Top rated doctors
    top_doctors = Doctor.objects.order_by('-rating')[:5]
    
    # Department distribution
    department_stats = Department.objects.annotate(
        doctor_count=Count('doctors'),
        appointment_count=Count('doctors__appointments')
    )
    
    context = {
        'total_appointments': total_appointments,
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_departments': total_departments,
        'pending': pending,
        'approved': approved,
        'completed': completed,
        'rejected': rejected,
        'cancelled': cancelled,
        'total_revenue': total_revenue,
        'avg_rating': round(avg_rating, 1),
        'total_reviews': total_reviews,
        'appointments_week': appointments_week,
        'top_doctors': top_doctors,
        'department_stats': department_stats,
    }
    
    return render(request, 'analytics/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def doctor_analytics(request):
    """Doctor performance analytics"""
    
    doctors = Doctor.objects.annotate(
        total_appointments=Count('appointments'),
        completed_appointments=Count('appointments', filter=Count('appointments__status', ['completed'])),
        avg_rating=Avg('ratings_received__rating'),
        total_patients=Count('appointments__patient', distinct=True)
    ).order_by('-total_appointments')
    
    return render(request, 'analytics/doctor_analytics.html', {
        'doctors': doctors
    })


@login_required
@user_passes_test(is_admin)
def patient_analytics(request):
    """Patient demographics and engagement analytics"""
    
    patients = Patient.objects.annotate(
        total_appointments=Count('appointments'),
        completed_appointments=Count('appointments', filter=Count('appointments__status', ['completed'])),
        avg_rating_given=Avg('ratings_given__rating')
    ).order_by('-total_appointments')
    
    # Statistics
    total_patients = Patient.objects.count()
    active_patients = Patient.objects.filter(appointments__status='completed').distinct().count()
    new_patients_month = Patient.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=30)
    ).count()
    
    context = {
        'patients': patients,
        'total_patients': total_patients,
        'active_patients': active_patients,
        'new_patients_month': new_patients_month,
    }
    
    return render(request, 'analytics/patient_analytics.html', context)


@login_required
@user_passes_test(is_admin)
def revenue_analytics(request):
    """Revenue and payment tracking"""
    
    completed_appointments = Appointment.objects.filter(status='completed')
    
    total_revenue = sum([
        float(apt.doctor.consultation_fee) for apt in completed_appointments
    ])
    
    # Revenue by doctor
    doctor_revenue = {}
    for apt in completed_appointments:
        doctor_key = f"{apt.doctor.user.first_name} {apt.doctor.user.last_name}"
        if doctor_key not in doctor_revenue:
            doctor_revenue[doctor_key] = 0
        doctor_revenue[doctor_key] += float(apt.doctor.consultation_fee)
    
    # Payment status
    paid = Appointment.objects.filter(payment_status='paid').count()
    unpaid = Appointment.objects.filter(payment_status='unpaid').count()
    refunded = Appointment.objects.filter(payment_status='refunded').count()
    
    context = {
        'total_revenue': total_revenue,
        'doctor_revenue': doctor_revenue,
        'paid': paid,
        'unpaid': unpaid,
        'refunded': refunded,
        'completed_appointments': completed_appointments.count(),
    }
    
    return render(request, 'analytics/revenue_analytics.html', context)


@login_required
@user_passes_test(is_admin)
def appointment_analytics(request):
    """Appointment trends and analysis"""
    
    # Status distribution
    statuses = {}
    for status in ['pending', 'approved', 'completed', 'rejected', 'cancelled', 'rescheduled']:
        statuses[status] = Appointment.objects.filter(status=status).count()
    
    # Monthly trends
    thirtydays_ago = timezone.now() - timedelta(days=30)
    monthly_appointments = Appointment.objects.filter(
        created_at__gte=thirtydays_ago
    ).count()
    
    # Average completion rate
    total_apts = Appointment.objects.count()
    completed_apts = Appointment.objects.filter(status='completed').count()
    completion_rate = (completed_apts / total_apts * 100) if total_apts > 0 else 0
    
    context = {
        'statuses': statuses,
        'monthly_appointments': monthly_appointments,
        'completion_rate': round(completion_rate, 1),
        'total_appointments': total_apts,
    }
    
    return render(request, 'analytics/appointment_analytics.html', context)
