import factory
from datetime import date, datetime

from ...models import PregnantFollowup

from .htc_subject_visit_factory import HtcSubjectVisitFactory


class PregnantFollowupFactory(factory.DjangoModelFactory):
    FACTORY_FOR = PregnantFollowup

    htc_subject_visit = factory.SubFactory(HtcSubjectVisitFactory)
    report_datetime = datetime.today()
    contact_consent = (('Yes', u'Yes'), ('No', u'No'))[0][0]
    contact_family = (('Yes', u'Yes'), ('No', u'No'))[0][0]