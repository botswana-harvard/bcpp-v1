from django.db import models
from datetime import date
from dateutil.relativedelta import relativedelta

from edc.device.sync.models import BaseSyncUuidModel
from edc.map.classes import site_mappers
from edc_base.audit_trail import AuditTrail
from edc_consent.models.fields import (
    ReviewFieldsMixin, SampleCollectionFieldsMixin, PersonalFieldsMixin,
    CitizenFieldsMixin, VulnerabilityFieldsMixin)
from edc_consent.models.fields.bw import IdentityFieldsMixin

from .clinic_off_study_mixin import ClinicOffStudyMixin
from .base_household_member_consent import BaseHouseholdMemberConsent


class ClinicConsent(BaseHouseholdMemberConsent, ClinicOffStudyMixin, PersonalFieldsMixin,
                    VulnerabilityFieldsMixin, SampleCollectionFieldsMixin, ReviewFieldsMixin,
                    IdentityFieldsMixin, CitizenFieldsMixin, BaseSyncUuidModel):
    """A model completed by the user to capture the ICF."""
    lab_identifier = models.CharField(
        verbose_name=("lab allocated identifier"),
        max_length=50,
        null=True,
        blank=True,
        help_text="if known."
    )

    htc_identifier = models.CharField(
        verbose_name=("HTC Identifier"),
        max_length=50,
        null=True,
        blank=True,
        help_text="if known."
    )

    pims_identifier = models.CharField(
        verbose_name=("PIMS identifier"),
        max_length=50,
        null=True,
        blank=True,
        help_text="if known."
    )

    history = AuditTrail()

    def save(self, *args, **kwargs):
        self.community = site_mappers.get_current_mapper().map_area
        super(ClinicConsent, self).save(*args, **kwargs)

    @property
    def age_at_consent(self):
        age_in_years = relativedelta(date.today(), self.dob).years
        years_since_consent = relativedelta(date.today(), self.consent_datetime).years
        return age_in_years - years_since_consent

    def is_dispatchable_model(self):
        return False

    class Meta:
        app_label = 'bcpp_clinic'
        verbose_name = 'Clinic Consent RBD'
        verbose_name_plural = 'Clinic Consent RBD'
