from django import forms
from edc.base.form.forms import BaseModelForm
from ..models import HouseholdHeadEligibility


class HouseholdHeadEligibilityForm(BaseModelForm):

    def clean(self):

        cleaned_data = self.cleaned_data
        self.instance.matches_household_member_values(forms.ValidationError)
        return super(HouseholdHeadEligibilityForm, self).clean()

    class Meta:
        model = HouseholdHeadEligibility