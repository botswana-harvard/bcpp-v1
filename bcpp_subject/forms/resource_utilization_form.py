from django import forms

from ..models import ResourceUtilization

from .base_subject_model_form import BaseSubjectModelForm


class ResourceUtilizationForm (BaseSubjectModelForm):

    def clean(self):
        cleaned_data = super(ResourceUtilizationForm, self).clean()

        if cleaned_data.get('money_spent') > 0 and not cleaned_data.get('medical_cover'):
            raise forms.ValidationError('If money was spent on medicines, were all of these '
                                        'covered by anyone else e.g. medical aid?')

        return cleaned_data

    class Meta:
        model = ResourceUtilization
        fields = '__all__'
