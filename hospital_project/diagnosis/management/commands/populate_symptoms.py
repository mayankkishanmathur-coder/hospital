from django.core.management.base import BaseCommand
from diagnosis.models import Symptom


class Command(BaseCommand):
    help = 'Populate database with predefined symptoms'

    def handle(self, *args, **options):
        symptoms_data = [
            ('Fever', 'General', 'Elevated body temperature'),
            ('Cough', 'Respiratory', 'Persistent cough'),
            ('Sore Throat', 'Respiratory', 'Pain in the throat'),
            ('Fatigue', 'General', 'Extreme tiredness'),
            ('Shortness of Breath', 'Respiratory', 'Difficulty breathing'),
            ('Chest Pain', 'Cardiovascular', 'Pain in the chest area'),
            ('Headache', 'Neurological', 'Pain in the head'),
            ('Runny Nose', 'Respiratory', 'Nasal discharge'),
            ('Sneezing', 'Respiratory', 'Involuntary nasal ejection'),
            ('Itchy Eyes', 'Eye', 'Itching sensation in the eyes'),
            ('Abdominal Pain', 'Digestive', 'Pain in the abdomen'),
            ('Nausea', 'Digestive', 'Feeling of sickness'),
            ('Vomiting', 'Digestive', 'Expelling stomach contents'),
            ('Diarrhea', 'Digestive', 'Loose bowel movements'),
            ('Palpitations', 'Cardiovascular', 'Irregular heartbeat sensation'),
            ('High Blood Pressure', 'Cardiovascular', 'Elevated BP readings'),
            ('Dizziness', 'Neurological', 'Feeling of lightheadedness'),
            ('Joint Pain', 'Musculoskeletal', 'Pain in joints'),
            ('Swelling', 'General', 'Body part enlargement'),
            ('Stiffness', 'Musculoskeletal', 'Limited movement'),
            ('Frequent Urination', 'Urinary', 'Excessive urination'),
            ('Excessive Thirst', 'General', 'Unquenchable thirst'),
            ('Neck Stiffness', 'Musculoskeletal', 'Stiff neck'),
            ('Swollen Lymph Nodes', 'Immune', 'Enlarged lymph nodes'),
            ('Night Sweats', 'General', 'Excessive sweating at night'),
            ('Skin Rash', 'Dermatological', 'Skin irritation'),
            ('Itching', 'Dermatological', 'Skin itching sensation'),
            ('Redness', 'Dermatological', 'Red skin appearance'),
            ('Tremors', 'Neurological', 'Involuntary shaking'),
            ('Slow Movement', 'Neurological', 'Reduced movement speed'),
            ('Memory Loss', 'Neurological', 'Difficulty remembering'),
            ('Confusion', 'Neurological', 'Mental confusion'),
            ('Anxiety', 'Psychological', 'Excessive worry'),
            ('Panic Attacks', 'Psychological', 'Sudden panic episodes'),
            ('Rapid Heartbeat', 'Cardiovascular', 'Faster than normal pulse'),
            ('Sweating', 'General', 'Excessive perspiration'),
            ('Depression', 'Psychological', 'Persistent sadness'),
            ('Loss of Interest', 'Psychological', 'Lack of interest in activities'),
            ('Sleep Issues', 'Neurological', 'Insomnia or sleep disturbance'),
        ]

        count = 0
        for name, category, description in symptoms_data:
            obj, created = Symptom.objects.get_or_create(
                name=name,
                defaults={
                    'category': category,
                    'description': description,
                    'is_active': True
                }
            )
            if created:
                count += 1

        self.stdout.write(
            self.style.SUCCESS(f'✓ Successfully populated {count} new symptoms')
        )
