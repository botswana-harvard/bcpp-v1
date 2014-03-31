from datetime import datetime, timedelta

from django.test import TestCase

from edc.lab.lab_profile.classes import site_lab_profiles
from edc.lab.lab_profile.exceptions import AlreadyRegistered as AlreadyRegisteredLabProfile
from edc.subject.lab_tracker.classes import site_lab_tracker
from edc.map.classes import site_mappers, Mapper

from apps.bcpp_household.helpers import ReplacementHelper
from apps.bcpp_household_member.models import HouseholdMember
from apps.bcpp_household_member.models import SubjectAbsentee
from apps.bcpp_household_member.constants import REFUSED, ABSENT
from apps.bcpp_household_member.tests.factories import SubjectRefusalFactory, SubjectAbsenteeEntryFactory
from apps.bcpp_survey.models import Survey
from apps.bcpp_lab.lab_profiles import BcppSubjectProfile
from apps.bcpp.app_configuration.classes import BcppAppConfiguration
from apps.bcpp_subject.visit_schedule import BcppSubjectVisitSchedule
from apps.bcpp_household_member.tests.factories import HouseholdMemberFactory
from apps.bcpp_household.models import Household, HouseholdStructure, HouseholdLog

from ..constants import NEVER_OCCUPIED, SEASONALLY_OCCUPIED, RARELY_OCCUPIED

from .factories import PlotFactory, HouseholdRefusalFactory, RepresentativeEligibilityFactory, HouseholdLogEntryFactory, HouseholdAssessmentFactory


class TestPlotMapper(Mapper):
    map_area = 'test_community11'
    map_code = '094'
    regions = []
    sections = []
    landmarks = []
    gps_center_lat = -25.033194
    gps_center_lon = 25.747139
    radius = 5.5
    location_boundary = ()
site_mappers.register(TestPlotMapper)


class PlotReplacementTests(TestCase):

    def setUp(self):
        try:
            site_lab_profiles.register(BcppSubjectProfile())
        except AlreadyRegisteredLabProfile:
            pass
        BcppAppConfiguration()
        site_lab_tracker.autodiscover()
        BcppSubjectVisitSchedule().build()

        self.survey1 = Survey.objects.get(survey_name='BCPP Year 1')  # see app_configuration

    def household_member_refused_factory(self, **kwargs):
        household_member = HouseholdMemberFactory(**kwargs)
        pk = household_member.pk
        household_member = HouseholdMember.objects.get(pk=pk)
        household_member.member_status = REFUSED
        household_member.save()
        household_member = HouseholdMember.objects.get(pk=pk)
        SubjectRefusalFactory(household_member=household_member)

    def household_member_absent_factory(self, **kwargs):
        household_member = HouseholdMemberFactory(**kwargs)
        pk = household_member.pk
        household_member = HouseholdMember.objects.get(pk=pk)
        household_member.member_status = ABSENT
        household_member.save()
        household_member = HouseholdMember.objects.get(pk=pk)
        subject_absentee = SubjectAbsentee.objects.get(household_member=household_member)
        SubjectAbsenteeEntryFactory(subject_absentee=subject_absentee)
        SubjectAbsenteeEntryFactory(subject_absentee=subject_absentee)
        SubjectAbsenteeEntryFactory(subject_absentee=subject_absentee)

    def test_replacement_plot1(self):
        plot = PlotFactory(
            community='test_community11',
            household_count=1,
            status='non_residential',
            eligible_members=3,
            description="A blue house with yellow screen wall",
            time_of_week='Weekdays',
            time_of_day='Morning',
            gps_degrees_s=25,
            gps_minutes_s=0.5666599,
            gps_degrees_e=25,
            gps_minutes_e=44.366660,
            selected=2,
            replaces='ERIK')
        replacement_helper = ReplacementHelper()
        self.assertEquals(replacement_helper.replaceable_plots(), [plot])

    def test_replacement_plot2(self):
        """Assert helper returns an empty list if plot is not replaceable."""
        PlotFactory(
            community='test_community11',
            household_count=0,
            status='non_residential',
            eligible_members=3,
            description="A blue house with yellow screen wall",
            time_of_week='Weekdays',
            time_of_day='Morning',
            gps_degrees_s=25,
            gps_minutes_s=0.5666599,
            gps_degrees_e=25,
            gps_minutes_e=44.366660,
            selected=2,)
        replacement_helper = ReplacementHelper()
        self.assertEquals(replacement_helper.replaceable_plots(), [])

    def test_replacement_plot3(self):
        """Assert helper returns an empty list if plot is not replaceable."""
        PlotFactory(
            community='test_community11',
            household_count=1,
            status='residential_habitable',
            eligible_members=3,
            description="A blue house with yellow screen wall",
            time_of_week='Weekdays',
            time_of_day='Morning',
            gps_degrees_s=25,
            gps_minutes_s=0.5666599,
            gps_degrees_e=25,
            gps_minutes_e=44.366660,
            selected=2,
            replaces='H12345')
        replacement_helper = ReplacementHelper()
        self.assertEquals(replacement_helper.replaceable_plots(), [])

    def test_refusal_household1(self):
        """Asserts that a household of refused members is replaceble."""
        plot = PlotFactory(
            community='test_community11',
            household_count=1,
            status='residential_habitable',
            eligible_members=3,
            description="A blue house with yellow screen wall",
            time_of_week='Weekdays',
            time_of_day='Morning',
            gps_degrees_s=25,
            gps_minutes_s=0.5666599,
            gps_degrees_e=25,
            gps_minutes_e=44.366660,
            selected=1)
        household = Household.objects.get(plot=plot)
        household_structure = HouseholdStructure.objects.get(household=household, survey=self.survey1)
        RepresentativeEligibilityFactory(household_structure=household_structure)
        household_member = HouseholdMember(
            household_structure=household_structure,
            first_name='COOL',
            initials='CC',
            gender='M',
            member_status=REFUSED,
            age_in_years=50,
            present_today='Yes',
            study_resident='Yes')
        household_member.save()
        self.assertEqual(household_member.member_status, REFUSED)
        SubjectRefusalFactory(household_member=household_member, reason='I don\'t have time', refusal_date=datetime.now())
        replacement_helper = ReplacementHelper()
        self.assertEquals(replacement_helper.replaceable_plots(), [])
        self.assertEquals(replacement_helper.replaceable_households(self.survey1), [household])

    def test_refusal_household1a(self):
        """Asserts that a household of refused members is replaceble but if deleted is not replaceable."""

        plot = PlotFactory(
            community='test_community11',
            household_count=1,
            status='residential_habitable',
            eligible_members=3,
            description="A blue house with yellow screen wall",
            time_of_week='Weekdays',
            time_of_day='Morning',
            gps_degrees_s=25,
            gps_minutes_s=0.5666599,
            gps_degrees_e=25,
            gps_minutes_e=44.366660,
            selected=1)
        household = Household.objects.get(plot=plot)
        household_structure = HouseholdStructure.objects.get(household=household, survey=self.survey1)
        RepresentativeEligibilityFactory(household_structure=household_structure)
        self.household_member_refused_factory(
            household_structure=household_structure,
            gender='M',
            age_in_years=50,
            present_today='Yes',
            study_resident='Yes')
        replacement_helper = ReplacementHelper()
        self.assertEquals(replacement_helper.replaceable_households(self.survey1), [household])

    def test_refusal_household2(self):
        """Asserts that a household of 3 refused members is replaceble."""

        plot = PlotFactory(
            community='test_community11',
            household_count=1,
            status='residential_habitable',
            eligible_members=3,
            description="A blue house with yellow screen wall",
            time_of_week='Weekdays',
            time_of_day='Morning',
            gps_degrees_s=25,
            gps_minutes_s=0.5666599,
            gps_degrees_e=25,
            gps_minutes_e=44.366660,
            selected=1)
        household = Household.objects.get(plot=plot)
        household_structure = HouseholdStructure.objects.get(household=household, survey=self.survey1)
        RepresentativeEligibilityFactory(household_structure=household_structure)
        self.household_member_refused_factory(
            household_structure=household_structure,
            gender='M',
            age_in_years=50,
            present_today='Yes',
            study_resident='Yes')
        self.household_member_refused_factory(
            household_structure=household_structure,
            gender='M',
            age_in_years=34,
            present_today='Yes',
            study_resident='Yes')
        self.household_member_refused_factory(
            household_structure=household_structure,
            gender='F',
            age_in_years=30,
            present_today='Yes',
            study_resident='Yes')
        replacement_helper = ReplacementHelper()
        self.assertEquals(replacement_helper.replaceable_households(self.survey1), [household])

    def test_refusal_household3(self):
        """Asserts that a household of 3 refused members and two ineligible members is replaceble."""
        plot = PlotFactory(
            community='test_community11',
            household_count=1,
            status='residential_habitable',
            eligible_members=3,
            description="A blue house with yellow screen wall",
            time_of_week='Weekdays',
            time_of_day='Morning',
            gps_degrees_s=25,
            gps_minutes_s=0.5666599,
            gps_degrees_e=25,
            gps_minutes_e=44.366660,
            selected=1)
        household = Household.objects.get(plot=plot)
        household_structure = HouseholdStructure.objects.get(household=household, survey=self.survey1)
        RepresentativeEligibilityFactory(household_structure=household_structure)
        self.household_member_refused_factory(
            household_structure=household_structure,
            gender='M',
            age_in_years=50,
            present_today='Yes',
            study_resident='Yes')
        self.household_member_refused_factory(
            household_structure=household_structure,
            gender='M',
            age_in_years=34,
            present_today='Yes',
            study_resident='Yes')
        self.household_member_refused_factory(
            household_structure=household_structure,
            gender='F',
            age_in_years=30,
            present_today='Yes',
            study_resident='Yes')
        HouseholdMemberFactory(
            household_structure=household_structure,
            gender='F',
            age_in_years=70,
            present_today='Yes',
            study_resident='Yes')
        HouseholdMemberFactory(
            household_structure=household_structure,
            gender='F',
            age_in_years=12,
            present_today='Yes',
            study_resident='Yes')
        replacement_helper = ReplacementHelper()
        self.assertEquals(replacement_helper.replaceable_households(self.survey1), [household])

    def test_refusal_household4(self):
        """Asserts that if 2 households in a plot, 1 household with 3 refused members, the household is replaceble."""
        plot = PlotFactory(
            community='test_community11',
            household_count=2,
            status='residential_habitable',
            eligible_members=3,
            description="A blue house with yellow screen wall",
            time_of_week='Weekdays',
            time_of_day='Morning',
            gps_degrees_s=25,
            gps_minutes_s=0.5666599,
            gps_degrees_e=25,
            gps_minutes_e=44.366660,
            selected=1)
        households = Household.objects.filter(plot=plot)
        household1 = households[0]
        household2 = households[1]
        household_structure1 = HouseholdStructure.objects.get(household=household1, survey=self.survey1)
        household_structure2 = HouseholdStructure.objects.get(household=household2, survey=self.survey1)
        RepresentativeEligibilityFactory(household_structure=household_structure1)
        RepresentativeEligibilityFactory(household_structure=household_structure2)
        self.household_member_refused_factory(
            household_structure=household_structure1,
            gender='M',
            age_in_years=50,
            present_today='Yes',
            study_resident='Yes')
        self.household_member_refused_factory(
            household_structure=household_structure1,
            gender='M',
            age_in_years=34,
            present_today='Yes',
            study_resident='Yes')
        self.household_member_refused_factory(
            household_structure=household_structure1,
            gender='F',
            age_in_years=30,
            present_today='Yes',
            study_resident='Yes')
        #hh2
        HouseholdMemberFactory(
            household_structure=household_structure2,
            gender='F',
            age_in_years=70,
            present_today='Yes',
            study_resident='Yes')
        HouseholdMemberFactory(
            household_structure=household_structure2,
            gender='F',
            age_in_years=12,
            present_today='Yes',
            study_resident='Yes')
        replacement_helper = ReplacementHelper()
        self.assertEquals(replacement_helper.replaceable_plots(), [])
        self.assertEquals(replacement_helper.replaceable_households(self.survey1), [household1])

    def test_refusal_household5(self):
        """Asserts that a household with 3 eligible members is not replaceble."""

        plot = PlotFactory(
            community='test_community11',
            household_count=2,
            status='residential_habitable',
            eligible_members=3,
            description="A blue house with yellow screen wall",
            time_of_week='Weekdays',
            time_of_day='Morning',
            gps_degrees_s=25,
            gps_minutes_s=0.5666599,
            gps_degrees_e=25,
            gps_minutes_e=44.366660,
            selected=1)
        households = Household.objects.filter(plot=plot)
        household1 = households[0]
        households[1]
        household_structure1 = HouseholdStructure.objects.get(household=household1, survey=self.survey1)
        RepresentativeEligibilityFactory(household_structure=household_structure1)
        HouseholdMemberFactory(
            household_structure=household_structure1,
            gender='M',
            age_in_years=50,
            present_today='Yes',
            study_resident='Yes')
        HouseholdMemberFactory(
            household_structure=household_structure1,
            gender='M',
            age_in_years=34,
            present_today='Yes',
            study_resident='Yes')
        HouseholdMemberFactory(
            household_structure=household_structure1,
            gender='F',
            age_in_years=30,
            present_today='Yes',
            study_resident='Yes')
        replacement_helper = ReplacementHelper()
        self.assertEquals(replacement_helper.replaceable_plots(), [])
        self.assertEquals(replacement_helper.replaceable_households(self.survey1), [])

    def test_refusal_household6(self):
        """Asserts that a household with a HOH who has refused is replaceble."""
        plot = PlotFactory(
            community='test_community11',
            household_count=2,
            status='residential_habitable',
            eligible_members=3,
            description="A blue house with yellow screen wall",
            time_of_week='Weekdays',
            time_of_day='Morning',
            gps_degrees_s=25,
            gps_minutes_s=0.5666599,
            gps_degrees_e=25,
            gps_minutes_e=44.366660,
            selected=1)
        households = Household.objects.filter(plot=plot)
        household1 = households[0]
        households[1]
        household_structure = HouseholdStructure.objects.get(household=household1, survey=self.survey1)
        HouseholdRefusalFactory(household_structure=household_structure, report_datetime=datetime.now(), reason='not_interested')
        replacement_helper = ReplacementHelper()
        self.assertEquals(replacement_helper.replaceable_households(self.survey1), [household1])

    def test_refusal_household7(self):
        """Asserts a plot with 2 households, A and B, where in household A the HOH has refused, A is replaceble."""
        plot = PlotFactory(
            community='test_community11',
            household_count=2,
            status='residential_habitable',
            eligible_members=3,
            description="A blue house with yellow screen wall",
            time_of_week='Weekdays',
            time_of_day='Morning',
            gps_degrees_s=25,
            gps_minutes_s=0.5666599,
            gps_degrees_e=25,
            gps_minutes_e=44.366660,
            selected=1)
        household1, household2 = Household.objects.filter(plot=plot)
        household_structure1 = HouseholdStructure.objects.get(household=household1, survey=self.survey1)
        household_structure2 = HouseholdStructure.objects.get(household=household2, survey=self.survey1)
        RepresentativeEligibilityFactory(household_structure=household_structure1)
        RepresentativeEligibilityFactory(household_structure=household_structure2)
        HouseholdMemberFactory(
            household_structure=household_structure2,
            gender='F',
            age_in_years=70,
            present_today='Yes',
            study_resident='Yes')
        HouseholdMemberFactory(
            household_structure=household_structure2,
            gender='F',
            age_in_years=24,
            present_today='Yes',
            study_resident='Yes')
        HouseholdRefusalFactory(household_structure=household_structure1, report_datetime=datetime.now(), reason='not_interested')
        replacement_helper = ReplacementHelper()
        self.assertEquals(replacement_helper.replaceable_households(self.survey1), [household1])

    def test_absentees_ineligibles1(self):
        """Asserts a household with 1 absent member and no other eligible members is replaceble"""
        plot = PlotFactory(
                community='test_community11',
                household_count=1,
                status='residential_habitable',
                eligible_members=3,
                description="A blue house with yellow screen wall",
                time_of_week='Weekdays',
                time_of_day='Morning',
                gps_degrees_s=25,
                gps_minutes_s=0.786540,
                gps_degrees_e=25,
                gps_minutes_e=44.8981199,
                selected=1)
        household = Household.objects.get(plot=plot)
        household_structure = HouseholdStructure.objects.get(household=household, survey=self.survey1)
        RepresentativeEligibilityFactory(household_structure=household_structure)
        self.household_member_absent_factory(
            household_structure=household_structure,
            gender='F',
            age_in_years=51,
            present_today='No',
            study_resident='Yes')
        replacement_helper = ReplacementHelper()
        self.assertEquals(replacement_helper.replaceable_households(self.survey1), [household])

    def test_absentees_ineligibles2(self):
        """Asserts a household multiple members that are absent that its replaceble."""
        plot = PlotFactory(
                community='test_community11',
                household_count=1,
                status='residential_habitable',
                eligible_members=3,
                description="A blue house with yellow screen wall",
                time_of_week='Weekdays',
                time_of_day='Morning',
                gps_degrees_s=25,
                gps_minutes_s=0.786540,
                gps_degrees_e=25,
                gps_minutes_e=44.8981199,
                selected=1)
        household = Household.objects.get(plot=plot)
        household_structure = HouseholdStructure.objects.get(household=household, survey=self.survey1)
        RepresentativeEligibilityFactory(household_structure=household_structure)
        self.household_member_absent_factory(
            household_structure=household_structure,
            gender='F',
            age_in_years=51,
            present_today='No',
            study_resident='Yes')
        self.household_member_absent_factory(
            household_structure=household_structure,
            gender='F',
            age_in_years=34,
            present_today='No',
            study_resident='Yes')
        self.household_member_absent_factory(
            household_structure=household_structure,
            gender='F',
            age_in_years=23,
            present_today='No',
            study_resident='Yes')
        replacement_helper = ReplacementHelper()
        self.assertEquals(replacement_helper.replaceable_households(self.survey1), [household])

    def test_absentees_ineligibles3(self):
        """Asserts a household 3 members absent and 2 not absent that is not replaceble."""
        plot = PlotFactory(
                community='test_community11',
                household_count=1,
                status='residential_habitable',
                eligible_members=3,
                description="A blue house with yellow screen wall",
                time_of_week='Weekdays',
                time_of_day='Morning',
                gps_degrees_s=25,
                gps_minutes_s=0.786540,
                gps_degrees_e=25,
                gps_minutes_e=44.8981199,
                selected=1)
        household = Household.objects.get(plot=plot)
        household_structure = HouseholdStructure.objects.get(household=household, survey=self.survey1)
        RepresentativeEligibilityFactory(household_structure=household_structure)
        self.household_member_absent_factory(
            household_structure=household_structure,
            gender='F',
            age_in_years=51,
            present_today='No',
            study_resident='Yes')
        self.household_member_absent_factory(
            household_structure=household_structure,
            gender='F',
            age_in_years=34,
            present_today='No',
            study_resident='Yes')
        self.household_member_absent_factory(
            household_structure=household_structure,
            gender='F',
            age_in_years=23,
            present_today='No',
            study_resident='Yes')
        HouseholdMemberFactory(
            household_structure=household_structure,
            gender='F',
            age_in_years=70,
            present_today='Yes',
            study_resident='Yes')
        HouseholdMemberFactory(
            household_structure=household_structure,
            gender='F',
            age_in_years=24,
            present_today='Yes',
            study_resident='Yes')
        replacement_helper = ReplacementHelper()
        self.assertEquals(replacement_helper.replaceable_households(self.survey1), [])

    def test_check_absentees_ineligibles4(self):
        """Asserts a household initially is not replaceable"""

        PlotFactory(
                community='test_community11',
                household_count=1,
                status='residential_habitable',
                eligible_members=3,
                description="A blue house with yellow screen wall",
                time_of_week='Weekdays',
                time_of_day='Morning',
                gps_degrees_s=25,
                gps_minutes_s=0.786540,
                gps_degrees_e=25,
                gps_minutes_e=44.8981199,
                selected=1)
        replacement_helper = ReplacementHelper()
        self.assertEquals(replacement_helper.replaceable_households(self.survey1), [])

    def test_absentees_ineligibles5(self):
        """Asserts a household without an informant after 3 enumeration attempt is replaceble if last_seen_home indicates 4_weeks_a_year"""
        plot = PlotFactory(
                community='test_community11',
                household_count=1,
                status='residential_habitable',
                eligible_members=3,
                description="A blue house with yellow screen wall",
                time_of_week='Weekdays',
                time_of_day='Morning',
                gps_degrees_s=25,
                gps_minutes_s=0.786540,
                gps_degrees_e=25,
                gps_minutes_e=44.8981199,
                selected=1)
        household = Household.objects.get(plot=plot)
        household_structure = HouseholdStructure.objects.get(household=household, survey=self.survey1)
        household_log = HouseholdLog.objects.get(household_structure=household_structure)
        HouseholdLogEntryFactory(household_log=household_log, household_status='no_household_informant', report_datetime=datetime.today() - timedelta(days=3))
        HouseholdLogEntryFactory(household_log=household_log, household_status='no_household_informant', report_datetime=datetime.today() - timedelta(days=2))
        HouseholdLogEntryFactory(household_log=household_log, household_status='no_household_informant', report_datetime=datetime.today() - timedelta(days=1))
        household_structure = HouseholdStructure.objects.get(household=household, survey=self.survey1)
        HouseholdAssessmentFactory(household_structure=household_structure, residency='No', last_seen_home=SEASONALLY_OCCUPIED)  # Status value becomes seasonally occupied
        replacement_helper = ReplacementHelper()
        self.assertEquals(replacement_helper.replaceable_households(self.survey1), [household])

    def test_absentees_ineligibles6(self):
        """Asserts a household without an informant after 3 enumeration attempt is replaceble if last_seen_home indicates 1_night_less_than_4_weeks_year"""
        plot = PlotFactory(
                community='test_community11',
                household_count=1,
                status='residential_habitable',
                eligible_members=3,
                description="A blue house with yellow screen wall",
                time_of_week='Weekdays',
                time_of_day='Morning',
                gps_degrees_s=25,
                gps_minutes_s=0.786540,
                gps_degrees_e=25,
                gps_minutes_e=44.8981199,
                selected=1)
        household = Household.objects.get(plot=plot)
        household_structure = HouseholdStructure.objects.get(household=household, survey=self.survey1)
        household_log = HouseholdLog.objects.get(household_structure=household_structure)
        HouseholdLogEntryFactory(household_log=household_log, household_status='no_household_informant', report_datetime=datetime.today() - timedelta(days=3))
        HouseholdLogEntryFactory(household_log=household_log, household_status='no_household_informant', report_datetime=datetime.today() - timedelta(days=2))
        HouseholdLogEntryFactory(household_log=household_log, household_status='no_household_informant', report_datetime=datetime.today() - timedelta(days=1))
        household_structure = HouseholdStructure.objects.get(household=household, survey=self.survey1)
        HouseholdAssessmentFactory(household_structure=household_structure, residency='No', last_seen_home=RARELY_OCCUPIED)  # Status value becomes rarely occupied
        replacement_helper = ReplacementHelper()
        self.assertEquals(replacement_helper.replaceable_households(self.survey1), [household])

    def test_absentees_ineligibles7(self):
        """Asserts a household without an informant after 3 enumeration attempt is NOT replaceble if last_seen_home indicates never_spent_1_day_over_a_year"""
        plot = PlotFactory(
                community='test_community11',
                household_count=1,
                status='residential_habitable',
                eligible_members=3,
                description="A blue house with yellow screen wall",
                time_of_week='Weekdays',
                time_of_day='Morning',
                gps_degrees_s=25,
                gps_minutes_s=0.786540,
                gps_degrees_e=25,
                gps_minutes_e=44.8981199,
                selected=1)
        household = Household.objects.get(plot=plot)
        household_structure = HouseholdStructure.objects.get(household=household, survey=self.survey1)
        household_log = HouseholdLog.objects.get(household_structure=household_structure)
        HouseholdLogEntryFactory(household_log=household_log, household_status='no_household_informant', report_datetime=datetime.today() - timedelta(days=3))
        HouseholdLogEntryFactory(household_log=household_log, household_status='no_household_informant', report_datetime=datetime.today() - timedelta(days=2))
        HouseholdLogEntryFactory(household_log=household_log, household_status='no_household_informant', report_datetime=datetime.today() - timedelta(days=1))
        household_structure = HouseholdStructure.objects.get(household=household, survey=self.survey1)
        HouseholdAssessmentFactory(household_structure=household_structure, residency='No', last_seen_home=NEVER_OCCUPIED)  # Status value becomes never occupied
        replacement_helper = ReplacementHelper()
        self.assertEquals(replacement_helper.replaceable_households(self.survey1), [])

    def test_absentees_ineligibles8(self):
        """Asserts a household without an informant after 3 enumeration attempt is not replaceble if last_seen_home is unknown"""
        plot = PlotFactory(
                community='test_community11',
                household_count=1,
                status='residential_habitable',
                eligible_members=3,
                description="A blue house with yellow screen wall",
                time_of_week='Weekdays',
                time_of_day='Morning',
                gps_degrees_s=25,
                gps_minutes_s=0.786540,
                gps_degrees_e=25,
                gps_minutes_e=44.8981199,
                selected=1)
        household = Household.objects.get(plot=plot)
        household_structure = HouseholdStructure.objects.get(household=household, survey=self.survey1)
        household_log = HouseholdLog.objects.get(household_structure=household_structure)
        HouseholdLogEntryFactory(household_log=household_log, household_status='no_household_informant', report_datetime=datetime.today() - timedelta(days=3))
        HouseholdLogEntryFactory(household_log=household_log, household_status='no_household_informant', report_datetime=datetime.today() - timedelta(days=2))
        HouseholdLogEntryFactory(household_log=household_log, household_status='no_household_informant', report_datetime=datetime.today() - timedelta(days=1))
        household_structure = HouseholdStructure.objects.get(household=household, survey=self.survey1)
        HouseholdAssessmentFactory(household_structure=household_structure, residency='No', last_seen_home='dont_know')  # Status value becomes None
        replacement_helper = ReplacementHelper()
        self.assertEquals(replacement_helper.replaceable_households(self.survey1), [])

    def test_absentees_ineligibles9(self):
        """Asserts a household without an informant after 2 enumeration attempts is not replaceble"""
        plot = PlotFactory(
                community='test_community11',
                household_count=1,
                status='residential_habitable',
                eligible_members=3,
                description="A blue house with yellow screen wall",
                time_of_week='Weekdays',
                time_of_day='Morning',
                gps_degrees_s=25,
                gps_minutes_s=0.786540,
                gps_degrees_e=25,
                gps_minutes_e=44.8981199,
                selected=1)
        household = Household.objects.get(plot=plot)
        household_structure = HouseholdStructure.objects.get(household=household, survey=self.survey1)
        household_log = HouseholdLog.objects.get(household_structure=household_structure)
        HouseholdLogEntryFactory(household_log=household_log, household_status='no_household_informant', report_datetime=datetime.today() - timedelta(days=3))
        HouseholdLogEntryFactory(household_log=household_log, household_status='no_household_informant', report_datetime=datetime.today() - timedelta(days=2))
        replacement_helper = ReplacementHelper()
        self.assertEquals(replacement_helper.replaceable_households(self.survey1), [])

    def test_absentees_ineligibles10(self):
        """Asserts a household without an informant after 1 enumeration attempt is not replaceble"""
        plot = PlotFactory(
                community='test_community11',
                household_count=1,
                status='residential_habitable',
                eligible_members=3,
                description="A blue house with yellow screen wall",
                time_of_week='Weekdays',
                time_of_day='Morning',
                gps_degrees_s=25,
                gps_minutes_s=0.786540,
                gps_degrees_e=25,
                gps_minutes_e=44.8981199,
                selected=1)
        household = Household.objects.get(plot=plot)
        household_structure = HouseholdStructure.objects.get(household=household, survey=self.survey1)
        household_log = HouseholdLog.objects.get(household_structure=household_structure)
        HouseholdLogEntryFactory(household_log=household_log, household_status='no_household_informant',)
        replacement_helper = ReplacementHelper()
        self.assertEquals(replacement_helper.replaceable_households(self.survey1), [])

    def test_check_absentees_ineligibles11(self):
        """Asserts a household with present member that is replaceble"""

        plot = PlotFactory(
                community='test_community11',
                household_count=1,
                status='residential_habitable',
                eligible_members=3,
                description="A blue house with yellow screen wall",
                time_of_week='Weekdays',
                time_of_day='Morning',
                gps_degrees_s=25,
                gps_minutes_s=0.786540,
                gps_degrees_e=25,
                gps_minutes_e=44.8981199,
                selected=1)
        household = Household.objects.get(plot=plot)
        household_structure = HouseholdStructure.objects.get(household=household, survey=self.survey1)
        household_log = HouseholdLog.objects.get(household_structure=household_structure)
        HouseholdLogEntryFactory(household_log=household_log, household_status='eligible_representative_present',)
        replacement_helper = ReplacementHelper()
        self.assertEquals(replacement_helper.replaceable_households(self.survey1), [])

    def test_absentees_ineligibles12(self):
        """Asserts a household with 3 household log entries the last 1 with present status that is replaceble"""

        plot = PlotFactory(
                community='test_community11',
                household_count=1,
                status='residential_habitable',
                eligible_members=3,
                description="A blue house with yellow screen wall",
                time_of_week='Weekdays',
                time_of_day='Morning',
                gps_degrees_s=25,
                gps_minutes_s=0.786540,
                gps_degrees_e=25,
                gps_minutes_e=44.8981199,
                selected=1)
        household = Household.objects.get(plot=plot)
        household_structure = HouseholdStructure.objects.get(household=household, survey=self.survey1)
        household_log = HouseholdLog.objects.get(household_structure=household_structure)
        HouseholdLogEntryFactory(household_log=household_log, household_status='no_household_informant', report_datetime=datetime.today() - timedelta(days=3))
        HouseholdLogEntryFactory(household_log=household_log, household_status='no_household_informant', report_datetime=datetime.today() - timedelta(days=2))
        HouseholdLogEntryFactory(household_log=household_log, household_status='eligible_representative_present', report_datetime=datetime.today() - timedelta(days=1))
        replacement_helper = ReplacementHelper()
        self.assertEquals(replacement_helper.replaceable_households(self.survey1), [])

    def test_absentees_ineligibles13(self):
        """Asserts a household with 3 enumeration attempts with no eligible representative present, that is replaceble"""

        plot = PlotFactory(
                community='test_community11',
                household_count=1,
                status='residential_habitable',
                eligible_members=3,
                description="A blue house with yellow screen wall",
                time_of_week='Weekdays',
                time_of_day='Morning',
                gps_degrees_s=25,
                gps_minutes_s=0.786540,
                gps_degrees_e=25,
                gps_minutes_e=44.8981199,
                selected=1)
        household = Household.objects.get(plot=plot)
        household_structure = HouseholdStructure.objects.get(household=household, survey=self.survey1)
        household_log = HouseholdLog.objects.get(household_structure=household_structure)
        HouseholdLogEntryFactory(household_log=household_log, household_status='eligible_representative_absent', report_datetime=datetime.today() - timedelta(days=3))
        HouseholdLogEntryFactory(household_log=household_log, household_status='eligible_representative_absent', report_datetime=datetime.today() - timedelta(days=2))
        HouseholdLogEntryFactory(household_log=household_log, household_status='eligible_representative_absent', report_datetime=datetime.today() - timedelta(days=1))
        replacement_helper = ReplacementHelper()
        self.assertEquals(replacement_helper.replaceable_households(self.survey1), [household])

    def test_absentees_ineligibles14(self):
        """Asserts a household with 1 enumeration attempts with no eligible representative present, that is replaceble"""

        plot = PlotFactory(
                community='test_community11',
                household_count=1,
                status='residential_habitable',
                eligible_members=3,
                description="A blue house with yellow screen wall",
                time_of_week='Weekdays',
                time_of_day='Morning',
                gps_degrees_s=25,
                gps_minutes_s=0.786540,
                gps_degrees_e=25,
                gps_minutes_e=44.8981199,
                selected=1)
        household = Household.objects.get(plot=plot)
        household_structure = HouseholdStructure.objects.get(household=household, survey=self.survey1)
        household_log = HouseholdLog.objects.get(household_structure=household_structure)
        HouseholdLogEntryFactory(household_log=household_log, household_status='eligible_representative_absent')
        replacement_helper = ReplacementHelper()
        self.assertEquals(replacement_helper.replaceable_households(self.survey1), [])

    def test_absentees_ineligibles15(self):
        """Asserts a household with 1 enumeration attempts with no eligible representative present, that is replaceble"""

        plot = PlotFactory(
                community='test_community11',
                household_count=1,
                status='residential_habitable',
                eligible_members=3,
                description="A blue house with yellow screen wall",
                time_of_week='Weekdays',
                time_of_day='Morning',
                gps_degrees_s=25,
                gps_minutes_s=0.786540,
                gps_degrees_e=25,
                gps_minutes_e=44.8981199,
                selected=1)
        household = Household.objects.get(plot=plot)
        household_structure = HouseholdStructure.objects.get(household=household, survey=self.survey1)
        household_log = HouseholdLog.objects.get(household_structure=household_structure)
        HouseholdLogEntryFactory(household_log=household_log, household_status='eligible_representative_absent', report_datetime=datetime.today() - timedelta(days=3))
        HouseholdLogEntryFactory(household_log=household_log, household_status='eligible_representative_absent', report_datetime=datetime.today() - timedelta(days=2))
        replacement_helper = ReplacementHelper()
        self.assertEquals(replacement_helper.replaceable_households(self.survey1), [])

    def test_absentees_ineligibles16(self):
        """Asserts a household with 3 enumeration attempts with 2 no household informant and no eligible representative present that is replaceble"""

        plot = PlotFactory(
                community='test_community11',
                household_count=1,
                status='residential_habitable',
                eligible_members=3,
                description="A blue house with yellow screen wall",
                time_of_week='Weekdays',
                time_of_day='Morning',
                gps_degrees_s=25,
                gps_minutes_s=0.786540,
                gps_degrees_e=25,
                gps_minutes_e=44.8981199,
                selected=1)
        household = Household.objects.get(plot=plot)
        household_structure = HouseholdStructure.objects.get(household=household, survey=self.survey1)
        household_log = HouseholdLog.objects.get(household_structure=household_structure)
        HouseholdLogEntryFactory(household_log=household_log, household_status='no_household_informant', report_datetime=datetime.today() - timedelta(days=3))
        HouseholdLogEntryFactory(household_log=household_log, household_status='no_household_informant', report_datetime=datetime.today() - timedelta(days=2))
        HouseholdLogEntryFactory(household_log=household_log, household_status='eligible_representative_absent', report_datetime=datetime.today() - timedelta(days=1))

        replacement_helper = ReplacementHelper()
        self.assertEquals(replacement_helper.replaceable_households(self.survey1), [household])

    def test_absentees_ineligibles17(self):
        """Asserts a household with 1 enumeration attempts with no eligible representative present, that is replaceble"""

        plot = PlotFactory(
                community='test_community11',
                household_count=1,
                status='residential_habitable',
                eligible_members=3,
                description="A blue house with yellow screen wall",
                time_of_week='Weekdays',
                time_of_day='Morning',
                gps_degrees_s=25,
                gps_minutes_s=0.786540,
                gps_degrees_e=25,
                gps_minutes_e=44.8981199,
                selected=1)
        household = Household.objects.get(plot=plot)
        household_structure = HouseholdStructure.objects.get(household=household, survey=self.survey1)
        household_log = HouseholdLog.objects.get(household_structure=household_structure)
        HouseholdLogEntryFactory(household_log=household_log, household_status='eligible_representative_absent',)
        replacement_helper = ReplacementHelper()
        self.assertEquals(replacement_helper.replaceable_households(self.survey1), [])
