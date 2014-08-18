from django import forms

from ..classes import SubjectReferralHelper
from ..models import SubjectReferral

from .base_subject_model_form import BaseSubjectModelForm


class SubjectReferralForm(BaseSubjectModelForm):

    def clean(self):
        cleaned_data = super(SubjectReferralForm, self).clean()
        subject_referral_helper = SubjectReferralHelper(SubjectReferral(**cleaned_data))
        if not subject_referral_helper.validate_referral_appt_date(forms.ValidationError) and not cleaned_data.get('comment'):
            raise forms.ValidationError('If you changed the default Referral Appointment Date, then you must give a comment as to why?')
        if subject_referral_helper.missing_data:
            raise forms.ValidationError('Some data is missing for the referral. Complete \'{0}\' first and try again.'.format(subject_referral_helper.missing_data._meta.verbose_name))
        return cleaned_data

    class Meta:
        model = SubjectReferral
