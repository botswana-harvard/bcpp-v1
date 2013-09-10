import factory
from bhp_base_model.tests.factories import BaseUuidModelFactory
from bcpp_household_member.models import HouseholdMember
# from bcpp_survey.tests.factories import SurveyFactory
from bcpp_household.tests.factories import HouseholdStructureFactory


class HouseholdMemberFactory(BaseUuidModelFactory):
    FACTORY_FOR = HouseholdMember

    first_name = factory.Sequence(lambda n: 'first_name{0}'.format(n))
    initials = factory.Sequence(lambda n: 'initials{0}'.format(n))
    gender = (('M', 'Male'), ('F', 'Female'))[0][0]
    age_in_years = 2
    present = (('Yes', 'Yes'), ('No', 'No'))[0][0]
    lives_in_household = (('Yes', 'Yes'), ('No', 'No'))[0][0]
    is_eligible_member = True
    target = 2
    #internal_identifier = registered_subject.registration_identifier
    #survey = factory.SubFactory(SurveyFactory)
    household_structure = factory.SubFactory(HouseholdStructureFactory)
    nights_out = 2
