from django.db import models
from django.utils.translation import ugettext as _

from edc.base.model.fields import OtherCharField
from edc.audit.audit_trail import AuditTrail

from ..managers import GrantManager
from ..choices import GRANT_TYPE

from .base_scheduled_inline_model import BaseScheduledInlineModel
from .labour_market_wages import LabourMarketWages


class Grant(BaseScheduledInlineModel):
    """Inline for labour_market_wages."""
    labour_market_wages = models.ForeignKey(LabourMarketWages)

    grant_number = models.IntegerField(
        verbose_name=_("How many of each type of grant do you receive?"),
        max_length=2,
        )
    grant_type = models.CharField(
        verbose_name=_("Grant name"),
        choices=GRANT_TYPE,
        max_length=50,
        )
    other_grant = OtherCharField()

    history = AuditTrail()

    objects = GrantManager()

    @property
    def inline_parent(self):
        return self.labour_market_wages

    def natural_key(self):
        return (self.report_datetime, ) + self.labour_market_wages.natural_key()  # 1st natural key might be wrong
    natural_key.dependencies = ['bcpp_subject.labourmarketwages', ]

    class Meta:
        app_label = 'bcpp_subject'
        verbose_name = "Grant"
        verbose_name_plural = "Grants"
