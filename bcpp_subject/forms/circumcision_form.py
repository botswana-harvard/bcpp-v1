from django import forms
from base_subject_model_form import BaseSubjectModelForm
from bcpp_subject.models import Circumcision, Uncircumcised, Circumcised


class CircumcisionForm (BaseSubjectModelForm):

    class Meta:
        model = Circumcision


class CircumcisedForm (BaseSubjectModelForm):
    
    def clean(self):

        cleaned_data = super(CircumcisedForm, self).clean()
        if cleaned_data.get('circumcised') == 'Yes' and not cleaned_data.get('health_benefits_smc'):
            raise forms.ValidationError('if \'YES\', what are the benefits of male circumcision?.')

        return cleaned_data

    class Meta:
        model = Circumcised


class UncircumcisedForm (BaseSubjectModelForm):
    def clean(self):

        cleaned_data = super(UncircumcisedForm, self).clean()
        if cleaned_data.get('circumcised') == 'Yes' and not cleaned_data.get('health_benefits_smc'):
            raise forms.ValidationError('if \'YES\', what are the benefits of male circumcision?.')
#         if cleaned_data.get('reason_circ') == 'OTHER' and not cleaned_data.get('reason_circ_other'):
#             raise forms.ValidationError('if \'OTHER\', provide other reason why participant has not yet been circumcised.')
        # validate other
        if cleaned_data.get('circumcision_day') == 'Yes, specify:' and not cleaned_data.get('circumcision_day_other'):
            raise forms.ValidationError('if \'YES\', specify the day preferred.')
        if cleaned_data.get('circumcision_week') == 'Yes, specify:' and not cleaned_data.get('circumcision_week_other'):
            raise forms.ValidationError('if \'YES\', specify the week preferred.')
        if cleaned_data.get('circumcision_year') == 'Yes, specify:' and not cleaned_data.get('circumcision_year_other'):
            raise forms.ValidationError('if \'YES\', specify the year preferred.')

        return cleaned_data

    class Meta:
        model = Uncircumcised
