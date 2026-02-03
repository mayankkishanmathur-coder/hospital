# Generated migration for adding severity levels and urgency flags

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diagnosis', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='symptom',
            name='severity',
            field=models.CharField(
                choices=[('mild', 'Mild'), ('moderate', 'Moderate'), ('severe', 'Severe')],
                default='moderate',
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name='symptom',
            name='is_urgent',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='diagnosisrecord',
            name='confidence_level',
            field=models.CharField(
                choices=[('low', 'Low (< 60%)'), ('medium', 'Medium (60-80%)'), ('high', 'High (> 80%)')],
                default='medium',
                editable=False,
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name='diagnosisrecord',
            name='has_urgent_symptoms',
            field=models.BooleanField(default=False),
        ),
    ]

