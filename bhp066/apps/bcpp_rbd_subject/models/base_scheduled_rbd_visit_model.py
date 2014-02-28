from datetime import datetime

from django.db import models

from edc.base.model.validators import datetime_not_before_study_start, datetime_not_future
from edc.entry_meta_data.managers import EntryMetaDataManager
from edc.subject.consent.models import BaseConsentedUuidModel
from edc.audit.audit_trail import AuditTrail

from apps.bcpp_household.models import Plot

from ..managers import ScheduledRBDModelManager

from .subject_visit_rbd import SubjectVisitRBD
from apps.bcpp_subject.models import SubjectOffStudyMixin


class BaseScheduledRBDVisitModel(SubjectOffStudyMixin, BaseConsentedUuidModel):

    """ Base model for all scheduled models (adds key to :class:`SubjectVisit`). """

    subject_visit_rbd = models.OneToOneField(SubjectVisitRBD)

    report_datetime = models.DateTimeField("Today's date",
        validators=[
            datetime_not_before_study_start,
            datetime_not_future, ],
        default=datetime.today(),
        )

    objects = ScheduledRBDModelManager()

    history = AuditTrail()

    entry_meta_data_manager = EntryMetaDataManager(SubjectVisitRBD)

    def natural_key(self):
        return self.get_visit().natural_key()

    def __unicode__(self):
        return unicode(self.get_visit())

    def get_report_datetime(self):
        return self.get_visit().report_datetime

    def get_subject_identifier(self):
        return self.get_visit().get_subject_identifier()

    def get_visit(self):
        return self.subject_visit_rbd

    def is_dispatched_item_within_container(self, using=None):
        return (('bcpp_household', 'plot'), 'subject_visit_rbd__household_member__household_structure__household__plot')

    def dispatch_container_lookup(self, using=None):
        return (Plot, 'subject_visit_rbd__household_member__household_structure__household__plot__plot_identifier')

    def deserialize_get_missing_fk(self, attrname):  #FIX ME, return subject visit
        retval = None
        if attrname == 'subject_visit_rbd':
            return self.subject_visit_rbd
        return retval

    class Meta:
        abstract = True