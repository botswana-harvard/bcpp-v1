from django.db import models
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError

from edc.audit.audit_trail import AuditTrail
from edc.core.crypto_fields.fields import EncryptedTextField, EncryptedCharField
from edc.base.model.fields import UUIDField
from edc.device.dispatch.models import BaseDispatchSyncUuidModel

from apps.bcpp_household.exceptions import AlreadyReplaced

from ..managers import HouseholdRefusalManager, HouseholdRefusalHistoryManager

from .household_structure import HouseholdStructure
from .plot import Plot


HOUSEHOLD_REFUSAL = (
    ('not_interested', 'Not Interested'),
    ('does_not_have_time', 'Does not have time'),
    ('dont_want_to_answer', 'Don\'t want to answer'),
    ('other', 'Other'),
)


class BaseHouseholdRefusal(BaseDispatchSyncUuidModel):

    household_structure = models.OneToOneField(HouseholdStructure)

    report_datetime = models.DateTimeField()

    reason = models.CharField(
        verbose_name=_('Please indicate the reason the household cannot be enumerated'),
        max_length=25,
        choices=HOUSEHOLD_REFUSAL)

    reason_other = EncryptedCharField(
        verbose_name=_('If Other, specify'),
        max_length=100,
        blank=True,
        null=True,
        )

    comment = EncryptedTextField(
        max_length=250,
        help_text=_("You may provide a comment here or leave BLANK."),
        blank=True,
        null=True,
        )

    def save(self, *args, **kwargs):
        if self.household_structure.household.replaced_by:
            raise AlreadyReplaced('Model {0}-{1} has its container replaced.'.format(self._meta.object_name, self.pk))
        if self.household_structure.enrolled:
            raise ValidationError('Household is enrolled.')
        self.household_structure.refused_enumeration = True
        self.household_structure.save()
        super(BaseHouseholdRefusal, self).save(*args, **kwargs)

    def dispatch_container_lookup(self, using=None):
        return (Plot, 'household_structure__household__plot__plot_identifier')

    def __unicode__(self):
        return unicode(self.household_structure) + '(' + unicode(self.report_datetime) + ')'

    class Meta:
        abstract = True


class HouseholdRefusal(BaseHouseholdRefusal):

    objects = HouseholdRefusalManager()

    history = AuditTrail()

    def natural_key(self):
        return self.household_structure.natural_key()
    natural_key.dependencies = ['bcpp_household.household_structure']

    class Meta:
        app_label = 'bcpp_household'
        ordering = ['household_structure', ]


class HouseholdRefusalHistory(BaseHouseholdRefusal):

    transaction = UUIDField()

    objects = HouseholdRefusalHistoryManager()

    history = AuditTrail()

    def natural_key(self):
        return (self.transaction, )

    class Meta:
        app_label = 'bcpp_household'
        ordering = ['household_structure', ]
