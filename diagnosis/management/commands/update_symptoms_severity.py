from django.core.management.base import BaseCommand
from diagnosis.models import Symptom


class Command(BaseCommand):
    help = 'Update symptoms with severity levels and urgency flags'

    def handle(self, *args, **options):
        # Define urgent symptoms (emergency warning signs)
        urgent_symptoms = [
            'Chest Pain', 'Severe Headache', 'Shortness of Breath',
            'Severe Abdominal Pain', 'Sudden Numbness', 'Loss of Consciousness',
            'Seizures', 'Confusion', 'Tremors', 'Severe Bleeding',
            'Hemoptysis', 'Acute Weakness', 'Severe Burns', 'Subarachnoid Hemorrhage',
            'Aortic Dissection', 'Myocardial Infarction', 'Pulmonary Embolism',
            'Acute Respiratory Distress', 'Sepsis', 'Anaphylaxis'
        ]
        
        # Severe symptoms
        severe_symptoms = [
            'Severe Cough', 'Severe Fatigue', 'Severe Body Aches', 'Severe Pain',
            'Difficulty Breathing', 'Severe Vomiting', 'Severe Diarrhea',
            'Acute Pancreatitis', 'Appendicitis', 'Severe Lower Back Pain',
            'Severe Shoulder Pain', 'Severe Rectal Pain', 'Severe Anal Pain',
            'Meningitis', 'Encephalitis', 'Bacterial Meningitis', 'Brain Tumor',
            'Stroke', 'Herniated Disc', 'Intestinal Obstruction',
            'Acute Hepatitis', 'Liver Cirrhosis', 'Kidney Stones'
        ]
        
        # Mild symptoms (common cold, minor issues)
        mild_symptoms = [
            'Runny Nose', 'Sneezing', 'Itchy Eyes', 'Itching', 'Nasal Congestion',
            'Bad Breath', 'Loose Teeth', 'Mild Headache', 'Minor Pain',
            'Slight Fever', 'Occasional Cough', 'Mild Itching', 'Mild Redness',
            'Minor Burns', 'Light Bleeding', 'Mild Weakness'
        ]
        
        updated = 0
        for symptom in Symptom.objects.all():
            old_severity = symptom.severity
            old_urgent = symptom.is_urgent
            
            # Set urgency flag
            if symptom.name in urgent_symptoms:
                symptom.is_urgent = True
                symptom.severity = 'severe'
            # Set severity levels
            elif symptom.name in severe_symptoms:
                symptom.severity = 'severe'
            elif symptom.name in mild_symptoms:
                symptom.severity = 'mild'
            else:
                symptom.severity = 'moderate'
            
            # Save if changed
            if old_severity != symptom.severity or old_urgent != symptom.is_urgent:
                symptom.save()
                updated += 1
                self.stdout.write(
                    f'Updated: {symptom.name} '
                    f'(Severity: {symptom.severity}, Urgent: {symptom.is_urgent})'
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'✓ Successfully updated {updated} symptoms')
        )
