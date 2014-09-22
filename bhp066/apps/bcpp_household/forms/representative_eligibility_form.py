from django.db.models import Max
from django.forms import ValidationError

from edc.base.form.forms import BaseModelForm

from ..constants import ELIGIBLE_REPRESENTATIVE_ABSENT
from ..models import RepresentativeEligibility, HouseholdLogEntry


class RepresentativeEligibilityForm(BaseModelForm):

    def clean(self):
        cleaned_data = super(RepresentativeEligibilityForm, self).clean()
        household_structure = cleaned_data.get('household_structure')
        try:
            report_datetime = HouseholdLogEntry.objects.filter(
                household_log__household_structure=household_structure
                ).aggregate(Max('report_datetime')).get('report_datetime__max')
            HouseholdLogEntry.objects.get(
                household_log__household_structure=household_structure,
                report_datetime=report_datetime,
                household_status=ELIGIBLE_REPRESENTATIVE_ABSENT)
            raise ValidationError('The eligible household representative is absent. See Household Log.')
        except HouseholdLogEntry.DoesNotExist:
            pass
        return cleaned_data

    class Meta:
        model = RepresentativeEligibility
