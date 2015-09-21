from django.db import models

from edc_base.audit_trail import AuditTrail

from bhp066.apps.bcpp.choices import YES_NO_UNSURE

from .base_scheduled_visit_model import BaseScheduledVisitModel
from .subject_consent import SubjectConsent


class Circumcision (BaseScheduledVisitModel):

    CONSENT_MODEL = SubjectConsent

    circumcised = models.CharField(
        verbose_name="Are you circumcised?",
        max_length=15,
        choices=YES_NO_UNSURE,
        help_text="")

    history = AuditTrail()

    class Meta:
        app_label = 'bcpp_subject'
        verbose_name = "Circumcision"
        verbose_name_plural = "Circumcision"
