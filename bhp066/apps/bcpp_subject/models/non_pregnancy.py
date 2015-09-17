from django.db import models
from django.utils.translation import ugettext_lazy as _

from edc_base.audit_trail import AuditTrail

from bhp066.apps.bcpp.choices import YES_NO_UNSURE

from .base_pregnancy import BasePregnancy


class NonPregnancy (BasePregnancy):

    """A model completed by the user for female participants who are not pregnant."""

    more_children = models.CharField(
        verbose_name=_("Do you wish to have a child now or in the future?"),
        max_length=25,
        choices=YES_NO_UNSURE,
        help_text="",
    )

    history = AuditTrail()

    class Meta:
        app_label = 'bcpp_subject'
        verbose_name = "Non Pregnancy"
        verbose_name_plural = "Non Pregnancy"
