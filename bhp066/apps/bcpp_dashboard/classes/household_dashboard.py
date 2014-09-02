from datetime import datetime, date

from django.db.models import Max
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

from edc.dashboard.base.classes import Dashboard

from apps.bcpp_household.models import (Household, HouseholdStructure, HouseholdLogEntry, HouseholdLog,
                                        HouseholdAssessment, HouseholdRefusal, RepresentativeEligibility)
from apps.bcpp_household.helpers import ReplacementHelper

from apps.bcpp_household_member.models import EnrollmentLoss
from apps.bcpp_household_member.models import HouseholdHeadEligibility, HouseholdMember, EnrollmentChecklist, HouseholdInfo, SubjectHtc
from apps.bcpp_survey.models import Survey
from django.core.exceptions import MultipleObjectsReturned


class HouseholdDashboard(Dashboard):

    view = 'household_dashboard'
    dashboard_name = 'Household Dashboard'
    dashboard_url_name = 'household_dashboard_url'
    base_fields = ('id', 'created', 'modified', 'user_created', 'user_modified', 'hostname_created', 'hostname_modified')

    def __init__(self, dashboard_type, dashboard_id, dashboard_model, dashboard_models=None, **kwargs):
        self._plot = None
        self._household = None
        self._household_members = None
        self._household_structure = None
        self._household_log = None
        self._household_assessment = None
        self._household_info = None
        self._household_refusal = None
        self._first_survey = None
        self._survey = None
        self._surveys = None
        self._mapper_name = None
        dashboard_type_list = ['household', 'household_structure']
        dashboard_models = {'household': Household, 'household_structure': HouseholdStructure}
        super(HouseholdDashboard, self).__init__(dashboard_type, dashboard_id,
                                                 dashboard_model, dashboard_type_list,
                                                 dashboard_models)
        self.first_name = kwargs.get('first_name')
        self.mapper_name = kwargs.get('mapper_name')

    def add_to_context(self):
        super(HouseholdDashboard, self).add_to_context()

        self.context.add(
            home='bcpp_survey',
            title='',  # 'A. Household Composition',
            household_meta=Household._meta,
            household_member_meta=HouseholdMember._meta,
            household_assessment_meta=HouseholdAssessment._meta,
            enrollment_loss_meta=EnrollmentLoss._meta,
            household_structure_meta=HouseholdStructure._meta,
            household_log_entry_meta=HouseholdLogEntry._meta,
            enrollment_checklist_meta=EnrollmentChecklist._meta,
            subject_htc_meta=SubjectHtc._meta,
            household_info_meta=HouseholdInfo._meta,
            household_refusal_meta=HouseholdRefusal._meta,
            household_refusal=self.household_refusal,
            household_head_eligibility_meta=HouseholdHeadEligibility._meta,
            household_head_eligibility=self.household_head_eligibility,
            representative_eligibility_meta=RepresentativeEligibility._meta,
            representative_eligibility=self.representative_eligibility,
            plot=self.household.plot,
            household_assessment=self.household_assessment,
            household=self.household,
            household_identifier=self.household.household_identifier,
            household_structure=self.household_structure,
            household_members=self.household_members,
            household_log=self.household_log,
            household_log_entries=self.household_log_entries,
            first_name=self.first_name,
            current_member_count=self.current_member_count,
            survey=self.survey,
            rendered_surveys=self.render_surveys(),
            allow_edit_members=self.allow_edit_members,
            has_household_log_entry=self.has_household_log_entry,
            lastest_household_log_entry_household_status=self.lastest_household_log_entry_household_status,
            replaceable=self.replaceable,
            household_info=self.household_info,
            eligible_hoh=self.eligible_hoh,
            mapper_name=self.mapper_name,
            subject_dashboard_url='subject_dashboard_url',
            household_dashboard_url=self.dashboard_url_name,
            )

    @property
    def has_household_log_entry(self):
        """Confirms there is an househol_log_entry for today."""
        today = date.today()
        has_household_log_entry = False
        if self.household_log:
            if HouseholdLogEntry.objects.filter(
                    household_log=self.household_log,
                    report_datetime__year=today.year,
                    report_datetime__month=today.month,
                    report_datetime__day=today.day).exists():
                has_household_log_entry = True
        return has_household_log_entry

    @property
    def household_assessment(self):
        try:
            household_assessment = HouseholdAssessment.objects.get(
                household_structure=self.household_structure)
        except HouseholdAssessment.DoesNotExist:
            household_assessment = None
        return household_assessment

    @property
    def household_info(self):
        try:
            household_info = HouseholdInfo.objects.get(
                household_structure=self.household_structure)
        except HouseholdInfo.DoesNotExist:
            household_info = None
        return household_info

    @property
    def household_refusal(self):
        try:
            household_refusal = HouseholdRefusal.objects.get(
                household_structure=self.household_structure)
        except HouseholdRefusal.DoesNotExist:
            household_refusal = None
        return household_refusal

    @property
    def lastest_household_log_entry_household_status(self):
        try:
            report_datetime = HouseholdLogEntry.objects.filter(
                household_log__household_structure=self.household_structure
                ).aggregate(Max('report_datetime')).get('report_datetime__max')
            lastest_household_log_entry = HouseholdLogEntry.objects.get(
                household_log__household_structure=self.household_structure,
                report_datetime=report_datetime)
            return lastest_household_log_entry.household_status
        except HouseholdLogEntry.DoesNotExist:
            return None

    @property
    def replaceable(self):
        replacement_helper = ReplacementHelper()
        replacement_helper.household_structure = self.household_structure
        return replacement_helper.replaceable

    @property
    def eligible_hoh(self):
        """Returns an instance of HouseholdHeadEligibility if there
        is a verified eligible Head of Household."""
        return self.household_head_eligibility

    @property
    def household_head_eligibility(self):
        """Returns an instance of HouseholdHeadEligibility if there
        is a verified eligible Head of Household."""
        try:
            household_head_eligibility = HouseholdHeadEligibility.objects.get(
                household_structure=self.household_structure)
        except HouseholdHeadEligibility.DoesNotExist:
            household_head_eligibility = None
        except MultipleObjectsReturned:
            # just get one
            household_head_eligibility = HouseholdHeadEligibility.objects.filter(
                household_structure=self.household_structure)[0]
        return household_head_eligibility

    @property
    def representative_eligibility(self):
        try:
            representative_eligibility = RepresentativeEligibility.objects.get(
                household_structure=self.household_structure)
        except RepresentativeEligibility.DoesNotExist:
            representative_eligibility = None
        return representative_eligibility

    @property
    def survey(self):
        """Returns the current survey."""
        return self.current_survey

    @property
    def current_survey(self):
        """Sets to the current survey using today's date."""
        current_survey = None
        try:
            current_survey = Survey.objects.get(datetime_start__lte=datetime.today(),
                                                datetime_end__gte=datetime.today())
        except Survey.DoesNotExist:
            raise Survey.DoesNotExist('Unable to set attribute _survey given survey=None and today\'s '
                                      'date. No survey exists to include the given datetime (today). '
                                      'Either create a new survey or update an existing survey\'s '
                                      'start and end date to include today.')
        except MultipleObjectsReturned:
            raise MultipleObjectsReturned('Unable to determine the current survey given survey=None and '
                                          'today\'s date. More than one survey exists for the given '
                                          'datetime (today). Either specify a survey or given a '
                                          'different date. Got {0}.'.format(
                                              Survey.objects.filter(datetime_start__lte=datetime.today(),
                                                                    datetime_end__gte=datetime.today()))
                                          )
        return current_survey

    @property
    def first_survey(self):
        """Returns the first survey and there should always be at least one."""
        if not self._first_survey:
            try:
                self._first_survey = Survey.objects.all().order_by('datetime_start', 'survey_name')[0]
            except IndexError:
                Survey.DoesNotExist('Unable to determine the first survey. Are any defined?')
        return self._first_survey

    @property
    def surveys(self):
        """Returns a list of surveys order by date excluding the current."""
        if not self._surveys:
            self._surveys = [(self.survey, '')]
            for survey in Survey.objects.all().exclude(pk=self.survey.pk).order_by('datetime_start'):
                household_structure = HouseholdStructure.objects.get(
                    household=self.household, survey=survey)
                url = reverse(self.dashboard_url_name,
                              kwargs={'dashboard_type': self.dashboard_type,
                                      'dashboard_model': 'household_structure',
                                      'dashboard_id': household_structure.pk})
                self._surveys.append((survey, url))
        return self._surveys

    @property
    def household_structure(self):
        """Sets the household_structure instance."""
        if not self._household_structure:
            if issubclass(self.dashboard_model, HouseholdStructure):
                self._household_structure = self.dashboard_model_instance
            elif issubclass(self.dashboard_model, Household):
                self._household_structure = HouseholdStructure.objects.get(
                    household__pk=self.household.pk, survey=self.survey)
        return self._household_structure

    @property
    def household(self):
        """Sets the household instance."""
        if not self._household:
            if isinstance(self.dashboard_model_instance, Household):
                self._household = self.dashboard_model_instance
            elif isinstance(self.dashboard_model_instance, HouseholdStructure):
                self._household = self.dashboard_model_instance.household
        return self._household

    @property
    def household_members(self):
        """Returns a queryset of household members for this household structure (and therefore survey)."""
        if not self._household_members:
            # TODO: this method needs to be verified for future surveys
            # self.create_household_members_for_new_survey()
            self._household_members = HouseholdMember.objects.filter(
                household_structure=self.household_structure,
                ).order_by('first_name')
        return self._household_members

    @property
    def household_log(self):
        """Returns the HouseholdLog and if it does not exist it will create one."""
        if not self._household_log:
            try:
                self._household_log = HouseholdLog.objects.get(
                    household_structure=self.household_structure)
            except HouseholdLog.DoesNotExist:
                self._household_log = None
        return self._household_log

    @property
    def current_member_count(self):
        try:
            return self.household_members.count()
        except AttributeError:
            return 0

    @property
    def allow_edit_members(self):
        allow_edit_members = False
        if not RepresentativeEligibility.objects.filter(
                household_structure=self.household_structure).exists():
            allow_edit_members = False
        elif hasattr(settings, 'ALLOW_CHANGES_OTHER_SURVEYS') and settings.ALLOW_CHANGES_OTHER_SURVEYS:
            allow_edit_members = True
        else:
            if self.survey:
                if self.survey.datetime_start <= datetime.today() and datetime.today() <= self.survey.datetime_end:
                    allow_edit_members = True
        return allow_edit_members

#     def check_members_have_registered_subject(self):
#         """Checks that a corresponding RegisteredSubject exists for each member in this household."""
#         for household_member in self.household_members:
#             if not RegisteredSubject.objects.filter(registration_identifier=household_member.internal_identifier):
#                 raise ValueError('{0} expects all household_members to have '
#                                  'an entry in RegisterSubject. Got None for {1}.'.format(self, household_member,))

    @property
    def household_log_entries(self):
        return HouseholdLogEntry.objects.filter(
            household_log__household_structure=self.household_structure)

    def create_household_members_for_new_survey(self):
        """ Prepares a householdstructure for a new survey by fetching a list of the
        householdstructure members for a given householdstructure from the FIRST
        survey and adds them to the new survey.

        ..todo:: This can be improved to check if someone has moved or died and
                 if there are members identified in interim surveys.
        """
        if self.first_survey:
            # add members from most recent first survey to current survey
            household_structure = HouseholdStructure.objects.get(
                household=self.household_structure.household, survey=self.first_survey)
            for hm in HouseholdMember.objects.filter(household_structure__household=household_structure.household):
                if not HouseholdMember.objects.filter(
                        household_structure=self.household_structure,
                        registered_subject=hm.registered_subject):
                    options = {}
                    [options.update({key: value}) for key, value in hm.__dict__.iteritems()
                     if not key.startswith('_') and key not in self.base_fields]
                    options.update({
                        'household_structure_id': self.household_structure.pk,
                        'registered_subject_id': hm.registered_subject.pk,
                        'survey_id': self.survey.pk,
                        'age_in_years': None,  # TODO: can this be incremented or at least accurate for consented subjects?
                        'nights_out': None,
                        'present': '-',
                        'lives_in_household': '-',
                        'member_status': None})
                    HouseholdMember.objects.create(**options)

    def render_surveys(self):
        """Renders to string the surveys."""
        return render_to_string('surveys.html', {'surveys': self.surveys, 'survey': self.survey})
