from django.db import models
from django.core.exceptions import ValidationError

from edc_base.model.models import HistoricalRecords
from edc_base.model.models import BaseUuidModel
from edc_constants.choices import YES_NO_DONT_KNOW

from ..managers import HouseholdAssessmentManager

from ..choices import RESIDENT_LAST_SEEN

from .household_structure import HouseholdStructure


class HouseholdAssessment(BaseUuidModel):
    """A model completed by the user to assess a household that could not
    be enumerated."""
    household_structure = models.OneToOneField(HouseholdStructure)

    potential_eligibles = models.CharField(
        verbose_name=('Research Assistant: From speaking with the respondent, is at least one'
                      'member of this plot potentially eligible?'),
        choices=YES_NO_DONT_KNOW,
        max_length=25,
        null=True,
        editable=True,
    )

    eligibles_last_seen_home = models.CharField(
        verbose_name=('When was a resident last seen in this household?'),
        choices=RESIDENT_LAST_SEEN,
        max_length=25,
        null=True,
        blank=True,
        editable=True,
    )

    def __str__(self):
        return str(self.household_structure)

    objects = HouseholdAssessmentManager()

    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        if self.household_structure.enumerated:
            raise ValidationError('HouseholdStructure has been enumerated')
        if self.household_structure.failed_enumeration_attempts < 3:
            raise ValidationError('Three attempts are required before Household Assessment')
        super(HouseholdAssessment, self).save(*args, **kwargs)

    def natural_key(self):
        return self.household_structure.natural_key()
    natural_key.dependencies = ['bcpp_household.household_structure']

    @property
    def vdc_househould_status(self):
        return self.last_seen_home

    class Meta:
        app_label = 'bcpp_household'
        verbose_name = 'Household Residency Status Assess'
        verbose_name_plural = 'Household Residency Status Assess'
