from django.db import models
from django.utils.translation import ugettext as _
from edc_lib.audit_trail.audit import AuditTrail
from edc_lib.bhp_base_model.fields import OtherCharField
from bcpp_list.models import LiveWith, Religion, EthnicGroups
from bcpp.choices import MARITALSTATUS_CHOICE
from base_scheduled_visit_model import BaseScheduledVisitModel


class Demographics (BaseScheduledVisitModel):

    """CS002"""

    religion = models.ManyToManyField(Religion,
        verbose_name=_("What is your religion affiliation?"),
        help_text="",
        )
    religion_other = OtherCharField()

    ethnic = models.ManyToManyField(EthnicGroups,
        verbose_name=_("What is your ethnic group?"),
        help_text="Ask for the original ethnic group",
        )
    other = OtherCharField()

    marital_status = models.CharField(
        verbose_name=_("What is your current marital status?"),
        max_length=55,
        choices=MARITALSTATUS_CHOICE,
        help_text="",
        )

    num_wives = models.IntegerField(
        verbose_name=_("How many wives does your husband have (including traditional marriage),"
                        " including yourself?"),
        max_length=2,
        null=True,
        blank=True,
        help_text="Leave blank if participant does not want to respond. (women only)",
        )
    husband_wives = models.IntegerField(
        verbose_name=_("How many wives do you have, including traditional marriage?"),
        max_length=2,
        null=True,
        blank=True,
        help_text="Leave blank if participant does not want to respond. (men only)",
        )

    live_with = models.ManyToManyField(LiveWith,
        verbose_name=_("Who do you currently live with ?"),
        help_text="[indicate all that apply]",
        )

    history = AuditTrail()

    class Meta:
        app_label = 'bcpp_subject'
        verbose_name = "Demographics"
        verbose_name_plural = "Demographics"
