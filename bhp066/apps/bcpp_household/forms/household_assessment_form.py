from django import forms
# from django.conf import settings
from edc.base.form.forms import BaseModelForm

from ..models import HouseholdAssessment


class HouseholdAssessmentForm(BaseModelForm):

    def clean(self):
        cleaned_data = self.cleaned_data

        if cleaned_data.get('potential_eligibles') == 'Yes':
            raise forms.ValidationError('Question 2 must be answer when question 1 answer is Yes.')
        return cleaned_data

    class Meta:
        model = HouseholdAssessment
