from django import forms
from base_subject_model_form import BaseSubjectModelForm
from bcpp_subject.models import Education


class EducationForm (BaseSubjectModelForm):

    def clean(self):
        cleaned_data = super(EducationForm, self).clean()
        # validating not working
        if cleaned_data.get('working', None) == 'No' and cleaned_data.get('job_type', None):
            raise forms.ValidationError('If participant is not working, do not give job type')
        if cleaned_data.get('working', None) == 'No' and not cleaned_data.get('reason_unemployed', None):
            raise forms.ValidationError('If participant is not working, provide reason for unemployment')
        # validating for those employed
        if cleaned_data.get('working', None) == 'Yes' and cleaned_data.get('reason_unemployed', None):
            raise forms.ValidationError('You have provided unemployment details yet have indicated that participant is working')
        if cleaned_data.get('working', None) == 'Yes' and not cleaned_data.get('job_type', None):
            raise forms.ValidationError('If participant is working, provide the job type')
        if cleaned_data.get('working', None) == 'Yes' and not cleaned_data.get('job_description', None):
            raise forms.ValidationError('If participant is employed, what is the job description')
        if cleaned_data.get('working', None) == 'Yes' and not cleaned_data.get('monthly_income', None):
            raise forms.ValidationError('If participant is employed, what is his/her monthly income?')
        return cleaned_data

    class Meta:
        model = Education
