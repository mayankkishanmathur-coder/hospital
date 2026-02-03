from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from appointments.models import Appointment
from patients.models import Patient


try:
    import stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY
    STRIPE_AVAILABLE = True
except:
    STRIPE_AVAILABLE = False


@login_required(login_url='patient_login')
def payment_page(request, appointment_id):
    """Display payment page for appointment"""
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        return redirect('patient_login')
    
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=patient)
    
    if appointment.payment_status == 'paid':
        return redirect('patient_dashboard')
    
    context = {
        'appointment': appointment,
        'amount': float(appointment.doctor.consultation_fee) * 100,  # Convert to cents
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'stripe_available': STRIPE_AVAILABLE,
    }
    
    return render(request, 'payments/payment_page.html', context)


@login_required(login_url='patient_login')
def process_payment(request, appointment_id):
    """Process payment using Stripe"""
    if not STRIPE_AVAILABLE:
        return redirect(f'/patients/appointment/{appointment_id}/')
    
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        return redirect('patient_login')
    
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=patient)
    
    if request.method == 'POST':
        try:
            token = request.POST.get('stripeToken')
            
            # Create a charge using the Stripe API
            charge = stripe.Charge.create(
                amount=int(float(appointment.doctor.consultation_fee) * 100),
                currency='usd',
                source=token,
                description=f'Appointment with {appointment.doctor} on {appointment.appointment_date}'
            )
            
            # Update appointment payment status
            appointment.payment_status = 'paid'
            appointment.payment_id = charge.id
            appointment.save()
            
            return redirect('payment_success', appointment_id=appointment.id)
        
        except stripe.error.CardError as e:
            context = {
                'appointment': appointment,
                'error': 'Your card was declined.',
            }
            return render(request, 'payments/payment_page.html', context)
        
        except stripe.error.RateLimitError:
            context = {
                'appointment': appointment,
                'error': 'Too many requests. Please try again.',
            }
            return render(request, 'payments/payment_page.html', context)
        
        except stripe.error.InvalidRequestError:
            context = {
                'appointment': appointment,
                'error': 'Invalid payment request.',
            }
            return render(request, 'payments/payment_page.html', context)
        
        except stripe.error.AuthenticationError:
            context = {
                'appointment': appointment,
                'error': 'Authentication failed.',
            }
            return render(request, 'payments/payment_page.html', context)
        
        except stripe.error.APIConnectionError:
            context = {
                'appointment': appointment,
                'error': 'Network error. Please try again.',
            }
            return render(request, 'payments/payment_page.html', context)
        
        except stripe.error.StripeError:
            context = {
                'appointment': appointment,
                'error': 'Payment processing failed. Please try again.',
            }
            return render(request, 'payments/payment_page.html', context)
    
    return redirect('payment_page', appointment_id=appointment.id)


@login_required(login_url='patient_login')
def payment_success(request, appointment_id):
    """Payment success page"""
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        return redirect('patient_login')
    
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=patient)
    
    return render(request, 'payments/payment_success.html', {
        'appointment': appointment,
    })


@login_required(login_url='patient_login')
def refund_appointment(request, appointment_id):
    """Request refund for appointment"""
    if not STRIPE_AVAILABLE:
        return redirect('patient_dashboard')
    
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        return redirect('patient_login')
    
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=patient)
    
    if appointment.payment_status != 'paid' or not appointment.payment_id:
        return redirect('patient_dashboard')
    
    if request.method == 'POST':
        try:
            # Process refund
            refund = stripe.Refund.create(
                charge=appointment.payment_id
            )
            
            # Update appointment status
            appointment.payment_status = 'refunded'
            appointment.status = 'cancelled'
            appointment.save()
            
            return redirect('patient_dashboard')
        
        except stripe.error.StripeError as e:
            context = {
                'appointment': appointment,
                'error': 'Refund processing failed. Please contact support.',
            }
            return render(request, 'payments/refund_page.html', context)
    
    return render(request, 'payments/refund_page.html', {
        'appointment': appointment,
    })


@login_required(login_url='patient_login')
def bills_and_payments(request):
    """Display all bills and payments for patient"""
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        return redirect('patient_login')
    
    from payments.models import Bill
    
    # Get all bills for the patient
    bills = Bill.objects.filter(patient=patient).order_by('-bill_date')
    
    # Calculate statistics
    total_bills = bills.count()
    paid_bills = bills.filter(payment_status='paid').count()
    unpaid_bills = bills.filter(payment_status__in=['unpaid', 'partial', 'overdue']).count()
    overdue_bills = bills.filter(payment_status='overdue').count()
    
    total_amount = sum(bill.total_amount for bill in bills)
    total_paid = sum(bill.paid_amount for bill in bills)
    total_due = sum(bill.remaining_amount for bill in bills if bill.payment_status != 'paid')
    
    # Filter by status if provided
    status_filter = request.GET.get('status', 'all')
    if status_filter != 'all':
        bills = bills.filter(payment_status=status_filter)
    
    context = {
        'bills': bills,
        'patient': patient,
        'total_bills': total_bills,
        'paid_bills': paid_bills,
        'unpaid_bills': unpaid_bills,
        'overdue_bills': overdue_bills,
        'total_amount': float(total_amount),
        'total_paid': float(total_paid),
        'total_due': float(total_due),
        'status_filter': status_filter,
    }
    
    return render(request, 'payments/bills_and_payments.html', context)

