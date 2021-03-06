from django import forms

from ..models import SubjectHtc

from edc_constants.constants import NOT_APPLICABLE


class SubjectHtcForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super(SubjectHtcForm, self).clean()
        if cleaned_data.get('offered') == 'Yes':
            self.offered_yes()
        else:
            self.offered_no()
        return cleaned_data

    def offered_yes(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get('offered') == 'Yes':
            if cleaned_data.get('accepted') == 'Yes' and cleaned_data.get('refusal_reason'):
                raise forms.ValidationError('You wrote HTC was accepted. A refusal reason is not applicable.')
            if cleaned_data.get('accepted') == 'No' and not cleaned_data.get('refusal_reason'):
                raise forms.ValidationError('You wrote HTC was not accepted. A refusal reason is required.')
            if cleaned_data.get('referred') == NOT_APPLICABLE:
                raise forms.ValidationError('Please indicate whether the subject was referred.')
            if cleaned_data.get('referred') == 'Yes' and not cleaned_data.get('referral_clinic'):
                raise forms.ValidationError('Please indicate the referral clinic.')
            if cleaned_data.get('referred') == 'No' and cleaned_data.get('referral_clinic'):
                raise forms.ValidationError('Subject was not referred. The referral clinic is not applicable.')

    def offered_no(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get('accepted') != NOT_APPLICABLE:
            raise forms.ValidationError(
                'Household member was not offered HTC. Whether subject accepted is not applicable.')
        if cleaned_data.get('refusal_reason'):
            raise forms.ValidationError('You wrote HTC was not offered. Refusal reason should be left blank.')
        if cleaned_data.get('referred') != NOT_APPLICABLE:
            raise forms.ValidationError(
                'Household member was not offered HTC. Whether subject was referred is not applicable.')
        if cleaned_data.get('referral_clinic'):
            raise forms.ValidationError(
                'Household member was not offered HTC. A referral clinic should be left blank.')

    class Meta:
        model = SubjectHtc
        fields = '__all__'
