import factory
from datetime import date, datetime
from edc.base.model.tests.factories import BaseUuidModelFactory
from bcpp_subject.models import SubjectUndecided
from bcpp_household_member.tests.factories import HouseholdMemberFactory
from bcpp_survey.tests.factories import SurveyFactory


class SubjectUndecidedFactory(BaseUuidModelFactory):
    FACTORY_FOR = SubjectUndecided

    household_member = factory.SubFactory(HouseholdMemberFactory)
    report_datetime = datetime.today()
    survey = factory.SubFactory(SurveyFactory)
