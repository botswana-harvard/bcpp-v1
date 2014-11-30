from django import forms

from edc.constants import NOT_APPLICABLE

from apps.bcpp_survey.models import Survey

from ..models import ResidencyMobility

from .base_subject_model_form import BaseSubjectModelForm


class ResidencyMobilityForm (BaseSubjectModelForm):

    def __init__(self, *args, **kwargs):
        super(ResidencyMobilityForm, self).__init__(*args, **kwargs)
        # customize for annual surveys
#         if Survey.objects.current_survey().datetime_start > Survey.objects.first_survey.survey_slug:
#             self.fields['permanent_resident'].help_text = (
#                 'If participant has moved into the community in the past 12 months, then since moving in '
#                 'has the participant typically spent more than 14 nights per month in this community.')
#             self.fields['permanent_resident'].label = (
#                 'Erik is a monkey')

    def clean(self):
        cleaned_data = super(ResidencyMobilityForm, self).clean()
        instance = None
        if self.instance.id:
            instance = self.instance
        else:
            instance = ResidencyMobility(**self.cleaned_data)
        # validating that residency status is not changed after capturing enrollment checklist
        instance.hic_enrollment_checks(forms.ValidationError)
        # validating residency + nights away. redmine 126
        if cleaned_data.get('permanent_resident') == 'Yes' and cleaned_data.get('nights_away') == 'more than 6 months':
            raise forms.ValidationError('If participant has spent 14 or more nights per month '
                                        'in this community, nights away can\'t be more than 6months.')
        # validating if other community, you specify
        if cleaned_data.get('cattle_postlands') == 'Other community' and not cleaned_data.get('cattle_postlands_other'):
            raise forms.ValidationError('If participant was staying in another community, specify the community')
        # this as in redmine issue 69
        if cleaned_data.get('nights_away') == 'zero' and cleaned_data.get('cattle_postlands') != NOT_APPLICABLE:
            raise forms.ValidationError(
                'If participant spent zero nights away, times spent away should be Not applicable')
        if cleaned_data.get('nights_away') != 'zero' and cleaned_data.get('cattle_postlands') == NOT_APPLICABLE:
            raise forms.ValidationError(
                'Participant has spent more than zero nights away, times spent away CANNOT be Not applicable')
        return cleaned_data

    class Meta:
        model = ResidencyMobility
