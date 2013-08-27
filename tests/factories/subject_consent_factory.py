import factory
from datetime import datetime
from bhp_consent.tests.factories import BaseConsentFactory
from bcpp_subject.models import SubjectConsent
#from bhp_variables.tests.factories import StudySiteFactory
from bcpp_household_member.tests.factories import HouseholdMemberFactory
from bcpp_survey.tests.factories import SurveyFactory


class SubjectConsentFactory(BaseConsentFactory):
    FACTORY_FOR = SubjectConsent

    subject_identifier = None  # factory.Sequence(lambda n: 'subject_identifier{0}'.format(n))
#     study_site = factory.SubFactory(StudySiteFactory)
    consent_datetime = datetime.today()
    may_store_samples = (('Yes', 'Yes'), ('No', 'No'))[0][0]
    is_incarcerated = (('Yes', 'Yes'), ('No', 'No'))[0][0]
    is_literate = (('Yes', 'Yes'), ('No', 'No'))[0][0]
    consent_version_on_entry = 1
    consent_version_recent = 1
    is_verified = True
    identity = factory.Sequence(lambda n: 'identity{0}'.format(n))
    identity_type = (('OMANG', 'Omang'), ('DRIVERS', "Driver's License"), ('PASSPORT', 'Passport'), ('OMANG_RCPT', 'Omang Receipt'), ('OTHER', 'Other'))[0][0]
    household_member = factory.SubFactory(HouseholdMemberFactory)
    survey = factory.SubFactory(SurveyFactory)
    is_signed = True
