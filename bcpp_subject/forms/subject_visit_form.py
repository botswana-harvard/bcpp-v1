from edc_core.bhp_consent.forms import BaseConsentedModelForm
from ..models import SubjectVisit


class SubjectVisitForm (BaseConsentedModelForm):

    class Meta:
        model = SubjectVisit
