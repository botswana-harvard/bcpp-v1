from django.core.urlresolvers import reverse
from django.db import models

from edc.audit.audit_trail import AuditTrail
from apps.bcpp_rbd.models import RBDVisit

from ..models import BaseSubjectRequisition
from ..managers import RequisitionManager


class SubjectRequisitionRBD(BaseSubjectRequisition):

    rbd_visit = models.ForeignKey(RBDVisit)

    entry_meta_data_manager = RequisitionManager(RBDVisit)

    history = AuditTrail()

    def save(self, *args, **kwargs):
        self.community = self.rbd_visit.household_member.household_structure.household.plot.community
        self.subject_identifier = self.get_visit().get_subject_identifier()
        super(SubjectRequisitionRBD, self).save(*args, **kwargs)

    def get_visit(self):
        return self.rbd_visit

    def dashboard(self):
        url = reverse('subject_dashboard_url',
                      kwargs={'dashboard_type': self.rbd_visit.appointment.registered_subject.subject_type.lower(),
                              'dashboard_model': 'appointment',
                              'dashboard_id': self.rbd_visit.appointment.pk,
                              'show': 'appointments'})
        return """<a href="{url}" />dashboard</a>""".format(url=url)
    dashboard.allow_tags = True

    class Meta:
        app_label = 'bcpp_lab'
        verbose_name = 'Blood Draw Only Requisition'
        unique_together = ('rbd_visit', 'panel', 'is_drawn')
