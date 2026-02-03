from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('patients', '0002_patient_blood_type_patient_emergency_contact_and_more'),
        ('doctors', '0002_department_doctor_bio_doctor_profile_image_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Symptom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('category', models.CharField(blank=True, max_length=50)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['category', 'name'],
            },
        ),
        migrations.CreateModel(
            name='DiagnosisRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('predicted_condition', models.CharField(max_length=200)),
                ('confidence_score', models.FloatField(default=0.0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('booked_doctor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='doctors.doctor')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='diagnosis_records', to='patients.patient')),
                ('predicted_specialization', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='doctors.doctorspecialization')),
                ('symptoms', models.ManyToManyField(related_name='diagnosis_records', to='diagnosis.symptom')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
