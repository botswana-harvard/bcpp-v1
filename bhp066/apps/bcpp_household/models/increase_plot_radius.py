from django.core.urlresolvers import reverse
from django.db import models

from edc.audit.audit_trail import AuditTrail
from edc.device.dispatch.models import BaseDispatchSyncUuidModel

from .plot import Plot


class IncreasePlotRadius(BaseDispatchSyncUuidModel):

    plot = models.OneToOneField(Plot)

    radius = models.FloatField(
        default=25.0,
        help_text='meters')

    history = AuditTrail()

    def __unicode__(self):
        return self.plot.plot_identifier

    def natural_key(self):
        return (self.plot.plot_identifier, )

    def dispatch_container_lookup(self):
        dispatch_container = models.get_model('dispatch', 'DispatchContainerRegister')
        if dispatch_container.objects.filter(
                container_identifier=self.plot.plot_identifier, is_dispatched=True).exists():
            return dispatch_container.objects.get(
                container_identifier=self.plot.plot_identifier, is_dispatched=True)
        return None

    def include_for_dispatch(self):
        return True

    @property
    def action(self):
        return self.plot.action

    @property
    def status(self):
        return self.plot.status

    class Meta:
        app_label = 'bcpp_household'
