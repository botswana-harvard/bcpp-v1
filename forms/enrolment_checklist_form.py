from django import forms
from bhp_base_form.forms import BaseModelForm
from bcpp_household_member.models import EnrolmentChecklist


class EnrolmentChecklistForm(BaseModelForm):

    def clean(self):
        cleaned_data = self.cleaned_data
        household_structure = cleaned_data.get('household_structure', None)
        if household_structure:
            if household_structure.is_dispatched_as_item():
                raise forms.ValidationError("Household is currently dispatched. Data may not be changed.")
        return cleaned_data

    class Meta:
        model = EnrolmentChecklist
