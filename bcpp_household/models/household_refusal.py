from django.db import models
from django.core.exceptions import ValidationError
from django_extensions.db.fields import UUIDField
from django_crypto_fields.fields import EncryptedTextField, EncryptedCharField
from simple_history.models import HistoricalRecords as AuditTrail

from edc_sync.model_mixins import SyncModelMixin
from edc_base.model.models import BaseUuidModel

from ..choices import HOUSEHOLD_REFUSAL
from ..managers import HouseholdRefusalManager, HouseholdRefusalHistoryManager

from .household_structure import HouseholdStructure
from .plot import Plot


class BaseHouseholdRefusal(SyncModelMixin, BaseUuidModel):

    household_structure = models.OneToOneField(HouseholdStructure)

    report_datetime = models.DateTimeField()

    reason = models.CharField(
        verbose_name='Please indicate the reason the household cannot be enumerated',
        max_length=25,
        choices=HOUSEHOLD_REFUSAL)

    reason_other = EncryptedCharField(
        verbose_name='If Other, specify',
        max_length=100,
        blank=True,
        null=True)

    comment = EncryptedTextField(
        max_length=250,
        help_text="You may provide a comment here or leave BLANK.",
        blank=True,
        null=True)

    def save(self, *args, **kwargs):
        if self.household_structure.enrolled:
            raise ValidationError('Household is enrolled.')
        super(BaseHouseholdRefusal, self).save(*args, **kwargs)

    def dispatch_container_lookup(self, using=None):
        return (Plot, 'household_structure__household__plot__plot_identifier')

    def __unicode__(self):
        return '{} ({})'.format(self.household_structure, self.report_datetime.strftime('%Y-%m-%d'))

    class Meta:
        abstract = True


class HouseholdRefusal(BaseHouseholdRefusal):
    """A model completed by the user to indicate the reason why a household
    cannot be enumerated."""
    objects = HouseholdRefusalManager()

    history = AuditTrail()

    def natural_key(self):
        return self.household_structure.natural_key()
    natural_key.dependencies = ['bcpp_household.household_structure']

    class Meta:
        app_label = 'bcpp_household'
        ordering = ['household_structure', ]


class HouseholdRefusalHistory(BaseHouseholdRefusal):
    """A system model to keep a history of deleted household refusal instances."""

    transaction = UUIDField()

    objects = HouseholdRefusalHistoryManager()

    history = AuditTrail()

    def natural_key(self):
        return (self.transaction, )

    class Meta:
        app_label = 'bcpp_household'
        ordering = ['household_structure', ]