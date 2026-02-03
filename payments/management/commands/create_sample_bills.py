from django.core.management.base import BaseCommand
from datetime import timedelta
from django.utils import timezone
from patients.models import Patient
from appointments.models import Appointment
from payments.models import Bill


class Command(BaseCommand):
    help = 'Create sample bills for patients'

    def handle(self, *args, **options):
        patients = Patient.objects.all()
        
        if not patients.exists():
            self.stdout.write(self.style.ERROR('No patients found'))
            return
        
        bill_types = ['consultation', 'diagnosis', 'procedure', 'follow_up', 'medication', 'service']
        payment_statuses = ['unpaid', 'paid', 'partial', 'overdue']
        
        bills_created = 0
        
        for patient in patients:
            # Create 3-5 bills per patient
            num_bills = 3 + (patient.id % 3)
            
            for i in range(num_bills):
                # Try to link to an appointment if available
                appointment = Appointment.objects.filter(patient=patient).first()
                
                bill_type = bill_types[i % len(bill_types)]
                payment_status = payment_statuses[i % len(payment_statuses)]
                
                amount = 50 + (i * 25)
                tax = amount * 0.1
                
                # Determine paid amount based on status
                if payment_status == 'paid':
                    paid_amount = amount + tax
                elif payment_status == 'partial':
                    paid_amount = (amount + tax) * 0.5
                else:
                    paid_amount = 0
                
                # Create bill
                bill = Bill.objects.create(
                    patient=patient,
                    appointment=appointment,
                    bill_type=bill_type,
                    description=f'Sample {bill_type.title()} for patient {patient.user.get_full_name()}',
                    amount=amount,
                    tax=tax,
                    paid_amount=paid_amount,
                    payment_status=payment_status,
                    due_date=timezone.now().date() + timedelta(days=30),
                    paid_date=timezone.now() if payment_status == 'paid' else None,
                    notes=f'Sample bill #{i+1}'
                )
                
                bills_created += 1
                self.stdout.write(self.style.SUCCESS(f'Created bill #{bill.id} for {patient.user.get_full_name()}'))
        
        self.stdout.write(self.style.SUCCESS(f'\nTotal bills created: {bills_created}'))
