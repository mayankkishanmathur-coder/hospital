# Test module for diagnosis app
from django.test import TestCase, Client
from django.contrib.auth.models import User
from patients.models import Patient
from doctors.models import Doctor, DoctorSpecialization
from diagnosis.models import Symptom, DiagnosisRecord
from diagnosis.ml_model import get_diagnosis_model


class DiagnosisModelTests(TestCase):
    """Test the ML model"""
    
    def test_model_loaded(self):
        """Test that model loads successfully"""
        model = get_diagnosis_model()
        assert model is not None, "Model should load"


class SymptomSeverityTests(TestCase):
    """Test symptom severity levels"""
    
    def test_symptom_severity_choices(self):
        """Test that symptom severity is properly set"""
        mild = Symptom.objects.create(name='Mild Symptom', severity='mild')
        moderate = Symptom.objects.create(name='Moderate Symptom', severity='moderate')
        severe = Symptom.objects.create(name='Severe Symptom', severity='severe')
        
        assert mild.severity == 'mild'
        assert moderate.severity == 'moderate'
        assert severe.severity == 'severe'


class DiagnosisRecordTests(TestCase):
    """Test diagnosis record model"""
    
    def setUp(self):
        from datetime import date
        self.user = User.objects.create_user(
            username='testpatient',
            password='testpass123'
        )
        self.patient = Patient.objects.create(
            user=self.user,
            phone='1234567890',
            date_of_birth=date(1990, 1, 1)
        )
        self.specialization = DoctorSpecialization.objects.create(
            name='General Practice'
        )
    
    def test_diagnosis_record_confidence_levels(self):
        """Test confidence level classification"""
        low_diagnosis = DiagnosisRecord.objects.create(
            patient=self.patient,
            predicted_condition='Low Confidence',
            predicted_specialization=self.specialization,
            confidence_score=0.50
        )
        assert low_diagnosis.confidence_level == 'low'
        
        high_diagnosis = DiagnosisRecord.objects.create(
            patient=self.patient,
            predicted_condition='High Confidence',
            predicted_specialization=self.specialization,
            confidence_score=0.90
        )
        assert high_diagnosis.confidence_level == 'high'
