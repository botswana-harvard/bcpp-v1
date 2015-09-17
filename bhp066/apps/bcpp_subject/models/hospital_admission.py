from django.db import models
from django.utils.translation import ugettext_lazy as _

from edc.audit.audit_trail import AuditTrail

from bhp066.apps.bcpp.choices import YES_NO_REFUSED

from ..choices import CARE_REASON, TRAVEL_HOURS

from .base_scheduled_visit_model import BaseScheduledVisitModel


class HospitalAdmission (BaseScheduledVisitModel):

    """A model completed by the user to capture information about hospital admissions"""

    admission_nights = models.IntegerField(
        verbose_name=_("How many total nights did you spend in the hospital in the past 3 months? "),
        max_length=2,
        null=True,
        blank=True,
        help_text="Note:If participant does not want to answer, leave blank",
    )
    reason_hospitalized = models.CharField(
        verbose_name=_("What was the primary reason for the most recent hospitalization in the past 3 months?"),
        max_length=95,
        null=True,
        blank=False,
        choices=CARE_REASON,
        default='None',
        help_text=" ",
    )
    facility_hospitalized = models.CharField(
        verbose_name=_("For this most recent hospitalization, where were you hospitalized? "),
        max_length=30,
        null=True,
        blank=True,
        help_text=" ",
    )
    nights_hospitalized = models.IntegerField(
        verbose_name=_("For this most recent hospitization, how many nights total did you"
                       " spend in the hospital? "),
        max_length=2,
        null=True,
        blank=True,
        help_text=" ",
    )
    healthcare_expense = models.DecimalField(
        verbose_name=_("How much did you have to pay to the healthcare provider"
                       " for the entire stay, including any medicines? "),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Pula",
    )
    travel_hours = models.CharField(
        verbose_name=_("For this most recent hospitalization, how long did it take you to get to the hospital? "),
        max_length=20,
        choices=TRAVEL_HOURS,
        null=True,
        blank=False,
        default='None',
        help_text=" ",
    )
    total_expenses = models.DecimalField(
        verbose_name=_("For this most recent hospitalization, how much did you have to pay for transport,"
                       " food and accommodation, including fuel if you used your own car? "),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Note:If participant does not want to answer, leave blank. Currency is Pula",
    )
    hospitalization_costs = models.CharField(
        verbose_name=_("For this most recent hospitalization, were any of these costs by covered by"
                       " anyone else, such as your medical aid or employer? "),
        max_length=17,
        choices=YES_NO_REFUSED,
        null=True,
        blank=True,
        help_text=" ",
    )

    history = AuditTrail()

    class Meta:
        app_label = 'bcpp_subject'
        verbose_name = "Hospital Admission"
        verbose_name_plural = "Hospital Admission"
