from django.db import models

from edc_base.model.validators import eligible_if_yes
from edc_constants.choices import YES_NO


class RepresentativeEligibilityMixin(models.Model):
    """Determines if the household member is eligible representative of the household."""

    aged_over_18 = models.CharField(
        verbose_name=("Did you verify that the respondent is aged 18 or older? "),
        max_length=10,
        choices=YES_NO,
        validators=[eligible_if_yes],
        help_text="If 'NO' respondent cannot serve as Household Head/Representative.",
    )

    household_residency = models.CharField(
        verbose_name=('Does the respondent typically spend more nights on average '
                      'in this household than in any other household in the same community?'),
        max_length=3,
        choices=YES_NO,
        help_text="If 'NO' respondent cannot serve as Household Head/Representative.",
    )

    verbal_script = models.CharField(
        verbose_name=("Did you administer the verbal script and ensure the respondent is willing "
                      "to provide household information? "),
        max_length=10,
        choices=YES_NO,
        validators=[eligible_if_yes],
        help_text="If 'NO' respondent cannot serve as Household Head/Representative.",
    )

    class Meta:
        abstract = True
