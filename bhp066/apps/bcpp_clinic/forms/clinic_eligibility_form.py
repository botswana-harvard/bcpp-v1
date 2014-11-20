from django import forms

from edc.base.form.forms import BaseModelForm

from ..models import ClinicEligibility


class ClinicEligibilityForm(BaseModelForm):

    def clean(self):
        cleaned_data = super(ClinicEligibilityForm, self).clean()
        try:
            if self.instance.is_consented:
                raise forms.ValidationError('Household member for this checklist has been consented. '
                                            'Eligibility checklist may not be edited')
        except AttributeError:
            pass
        if cleaned_data.get('has_identity') == 'No' and cleaned_data.get('identity'):
            raise forms.ValidationError('You indicated the patient did not provide '
                                        'an identity but identity is provided. Please correct.')

        return cleaned_data

    class Meta:
        model = ClinicEligibility
