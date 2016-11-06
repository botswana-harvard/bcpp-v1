from django.apps import apps as django_apps

from .base_household_member_manager import BaseHouseholdMemberManager


class MemberAppointmentManager(BaseHouseholdMemberManager):

    def get_by_natural_key(self, label, household_identifier, survey_name, subject_identifier_as_pk):
        HouseholdMember = django_apps.get_model('bcpp_household_member', 'HouseholdMember')
        household_member = HouseholdMember.objects.get_by_natural_key(
            household_identifier, survey_name, subject_identifier_as_pk)
        return self.get(label=label, household_member=household_member)
