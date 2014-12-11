from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import ugettext_lazy as _

from edc.audit.audit_trail import AuditTrail

from apps.bcpp.choices import YES_NO_REFUSED

from .base_scheduled_visit_model import BaseScheduledVisitModel


class ResourceUtilization (BaseScheduledVisitModel):

    """A model completed by the user to capture information about participants
    use of resources to obtain medical care."""

    out_patient = models.CharField(
        verbose_name=_("In the last 3 months, have you sought outpatient medical care for yourself?"
                       " Not including any visits for which you were hospitalized. "),
        max_length=17,
        choices=YES_NO_REFUSED,
        )
    hospitalized = models.IntegerField(
        verbose_name=_("In the last 3 months, how many times were you admitted to hospital or"
                       " other types of inpatient care and stayed one or more nights? This could be"
                       " a government, private, or church/mission hospital. "),
        max_length=2,
        null=True,
        help_text="",
        )
    money_spent = models.DecimalField(
        verbose_name=_("In the last 3 months, how much money in total have you spent on "
                       "medicines for yourself?"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(1000000000)],
        help_text="",
        )
    medical_cover = models.CharField(
        verbose_name=_("Were any of these costs for medicines or special foods covered"
                       " by anyone else, such as your medical aid or employer? "),
        max_length=17,
        choices=YES_NO_REFUSED,
        null=True,
        blank=True,
        help_text="",
        )

    history = AuditTrail()

    class Meta:
        app_label = 'bcpp_subject'
        verbose_name = "Resource Utilization Costs"
        verbose_name_plural = "Resource Utilization Costs"
