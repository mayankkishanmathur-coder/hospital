from django import forms
from .models import Symptom


class DiagnosisForm(forms.Form):
    """Form for symptom selection and diagnosis with custom symptom input"""
    
    SYMPTOM_CHOICES = (
        ('yes', 'Yes - Present'),
        ('no', 'No - Not Present'),
    )
    
    # Common moderate symptoms to show
    COMMON_MODERATE_SYMPTOMS = ['Fever', 'Cough', 'Headache', 'Fatigue', 'Nausea', 'Dizziness', 'Sore Throat']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Get symptoms filtered by severity and common status
        all_symptoms = Symptom.objects.filter(is_active=True)
        
        # Show: Severe + Urgent + Common Moderate symptoms only
        display_symptoms = (
            all_symptoms.filter(severity='severe') | 
            all_symptoms.filter(is_urgent=True) |
            all_symptoms.filter(name__in=self.COMMON_MODERATE_SYMPTOMS)
        ).order_by('severity', 'name').distinct()
        
        for symptom in display_symptoms:
            field_name = f'symptom_{symptom.id}'
            severity_display = symptom.get_severity_display()
            urgent_suffix = " [URGENT]" if symptom.is_urgent else ""
            label = f"{symptom.name} ({severity_display}){urgent_suffix}"
            
            self.fields[field_name] = forms.ChoiceField(
                choices=[('', '-- Not Selected --')] + list(self.SYMPTOM_CHOICES),
                required=False,
                widget=forms.RadioSelect(attrs={
                    'class': 'form-check-input',
                    'data-symptom': symptom.name,
                    'data-symptom-id': symptom.id,
                    'data-severity': symptom.severity,
                    'data-urgent': 'true' if symptom.is_urgent else 'false'
                }),
                label=label,
                help_text=symptom.description if symptom.description else None
            )
        
        # Add custom symptom text input
        self.fields['other_symptoms'] = forms.CharField(
            required=False,
            widget=forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter any other symptoms you are experiencing (comma-separated or in any format).\nExample: running nose, sore throat, weakness, body ache',
                'style': 'resize: vertical; font-size: 14px;'
            }),
            label='Other Symptoms (Optional)',
            help_text='Describe any additional symptoms not listed above. Our system will extract relevant keywords to improve diagnosis.'
        )
    
    def get_selected_symptoms(self):
        """Extract selected symptoms from form data"""
        selected_symptoms = []
        for field_name, value in self.cleaned_data.items():
            if field_name.startswith('symptom_') and value == 'yes':
                # Get the actual symptom name from widget attrs
                field = self.fields[field_name]
                symptom_name = field.widget.attrs.get('data-symptom', '')
                if symptom_name:
                    selected_symptoms.append(symptom_name)
        return selected_symptoms
    
    def get_other_symptoms_as_keywords(self):
        """Extract keywords from other symptoms text input with better matching"""
        other_text = self.cleaned_data.get('other_symptoms', '').lower().strip()
        if not other_text:
            return []
        
        # Get all available symptoms from database
        all_symptoms = list(Symptom.objects.filter(is_active=True).values_list('name', flat=True))
        
        matched_keywords = []
        
        # Check each symptom to see if it appears in the input text
        for symptom in all_symptoms:
            symptom_lower = symptom.lower()
            
            # Check for exact word match or phrase match
            import re
            
            # Try exact phrase match first (whole word boundaries)
            pattern = r'\b' + re.escape(symptom_lower) + r'\b'
            if re.search(pattern, other_text):
                if symptom not in matched_keywords:
                    matched_keywords.append(symptom)
                continue
            
            # Try substring match for compound symptoms
            if symptom_lower in other_text:
                if symptom not in matched_keywords:
                    matched_keywords.append(symptom)
        
        return matched_keywords
    
    def get_symptom_severity_info(self):
        """Get severity and urgency info for selected symptoms"""
        severity_info = {'mild': 0, 'moderate': 0, 'severe': 0, 'urgent': 0}
        for field_name, value in self.cleaned_data.items():
            if field_name.startswith('symptom_') and value == 'yes':
                field = self.fields[field_name]
                severity = field.widget.attrs.get('data-severity', 'moderate')
                is_urgent = field.widget.attrs.get('data-urgent', 'false') == 'true'
                
                severity_info[severity] += 1
                if is_urgent:
                    severity_info['urgent'] += 1
        return severity_info

