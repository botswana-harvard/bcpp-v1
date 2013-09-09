import factory
from datetime import date, datetime
from bhp_base_model.tests.factories import BaseUuidModelFactory
from bcpp_htc_subject.models import CircumcisionAppointment
from htc_subject_visit_factory import HtcSubjectVisitFactory


class CircumcisionAppointmentFactory(BaseUuidModelFactory):
    FACTORY_FOR = CircumcisionAppointment

    htc_subject_visit = factory.SubFactory(HtcSubjectVisitFactory)
    report_datetime = datetime.today()
    circumcision_ap = (('Yes', u'Yes'), ('No', u'No'))[0][0]
