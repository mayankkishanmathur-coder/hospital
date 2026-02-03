from django.core.management.base import BaseCommand
from appointments.models import Appointment
from appointments.notifications import send_appointment_reminder


class Command(BaseCommand):
    help = 'Send appointment reminders for appointments scheduled in next 24 hours'

    def handle(self, *args, **options):
        # Get appointments where reminder needs to be sent
        pending_reminders = Appointment.objects.filter(
            status='approved',
            reminder_sent=False
        )

        count = 0
        for appointment in pending_reminders:
            if appointment.is_reminder_due():
                send_appointment_reminder(appointment)
                appointment.mark_reminder_sent()
                count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully sent {count} appointment reminders')
        )
