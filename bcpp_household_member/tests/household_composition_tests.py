from datetime import datetime
from django.contrib import admin
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase

from edc.lab.lab_profile.classes import site_lab_profiles
from edc.lab.lab_profile.exceptions import AlreadyRegistered as AlreadyRegisteredLabProfile
from edc_map.site_mappers import site_mappers
from edc.subject.lab_tracker.classes import site_lab_tracker

from bhp066.apps.bcpp.app_configuration.classes import BcppAppConfiguration
from bhp066.apps.bcpp_household.models import HouseholdStructure, Household
from bhp066.apps.bcpp_household.tests.factories import HouseholdStructureFactory, PlotFactory, HouseholdFactory
from bhp066.apps.bcpp_lab.lab_profiles import BcppSubjectProfile
from bhp066.apps.bcpp_subject.visit_schedule import BcppSubjectVisitSchedule
from bhp066.apps.bcpp_survey.models import Survey
from bhp066.apps.bcpp_survey.tests.factories import SurveyFactory

from .factories import HouseholdMemberFactory


class HouseholdCompositionTests(TestCase):

    app_label = 'bcpp_household_member'

    def setUp(self):
        try:
            site_lab_profiles.register(BcppSubjectProfile())
        except AlreadyRegisteredLabProfile:
            pass
        BcppAppConfiguration()
        site_lab_tracker.autodiscover()
        BcppSubjectVisitSchedule().build()

        self.survey1 = Survey.objects.get(survey_name='BCPP Year 1')  # see app_configuration
        plot = PlotFactory(community='test_community3', household_count=1, status='residential_habitable')
        household = Household.objects.get(plot=plot)
        self.household_structure = HouseholdStructure.objects.get(household=household, survey=self.survey1)
        admin.autodiscover()
        site_lab_tracker.autodiscover()

    def test_p1(self):

        adminuser = User.objects.create_user('django', 'django@test.com', 'pass')
        adminuser.save()
        adminuser.is_staff = True
        adminuser.is_active = True
        adminuser.is_superuser = True
        adminuser.save()
        self.client.login(username=adminuser.username, password='pass')

        survey1 = SurveyFactory()
        survey2 = SurveyFactory()
        site_mappers.autodiscover()
        mapper = site_mappers.get(site_mappers.get_as_list()[0])
        self.assertEqual(Household.objects.all().count(), 0)
        plot = PlotFactory(community=mapper().get_map_area())
        plot.save()
        household = HouseholdFactory(plot=plot)
        self.assertRaises(IntegrityError, HouseholdStructureFactory, household=household, survey=survey1)
        household_structure1 = HouseholdStructure.objects.get(household=household, survey=survey1)
        hm1 = HouseholdMemberFactory(household_structure=household_structure1, first_name='ERIK', initials='EW')
        hm2 = HouseholdMemberFactory(household_structure=household_structure1, first_name='ERIK', initials='E1W')
        hm3 = HouseholdMemberFactory(household_structure=household_structure1, first_name='ERIK', initials='E2W')
        hm1.save()
        hm2.save()
        hm3.save()
        household.save()
        self.assertRaises(IntegrityError, HouseholdStructureFactory, household=household, survey=survey2)
        household_structure2 = HouseholdStructure.objects.get(household=household, survey=survey2)
        self.assertNotEqual(household_structure1, household_structure2)
        HouseholdMemberFactory(household_structure=household_structure2)
        HouseholdMemberFactory(household_structure=household_structure2, first_name='ERIK', initials='E1W')
        HouseholdMemberFactory(household_structure=household_structure2, first_name='ERIK', initials='E2W')
        HouseholdMemberFactory(household_structure=household_structure2, first_name='ERIK', initials='EW')
        hm1.save()
        hm2.save()
        hm3.save()
