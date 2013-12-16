from django.db.models import Count
from django.db.models import Q

from apps.bcpp_household_member.models.household_member import HouseholdMember
from apps.bcpp_subject.models.subject_consent import SubjectConsent
from .household_report_query import HouseholdReportQuery


class HouseholdMemberReportQuery(object):
    def __init__(self, community):
        self.community = community
        self.community_members = HouseholdMember.objects.filter(household_structure__household__community=community)
        self.refused = self.refused_qs().count()
        self.first_time_testers = self.first_time_testers_qs().count()
        self.tested = self.tested_qs().count()
        self.age_eligible = self.age_eligible_qs().count()
        self.study_eligible = self.study_eligible_qs()
        self.unreached_after_2_visits = self.unreached_after_visits_qs(2).count()
        self.hiv_positives = self.hiv_positive_qs().count()
        self.new_infections = self.new_infections_qs().count()
        self.already_infected = self.already_infected_qs().count()
        self.self_reported_infected = self.self_reported_positive_qs().count()

    def refused_qs(self):
        return self.community_members.filter(member_status='REFUSED')

    def absentee_stratified(self):
        absentee_strat = {}
        absentee_strat['absentees'] = self.absentee_qs().count()
        absentee_strat['visit_1'] = self.unreached_after_visits_qs(1).count()
        absentee_strat['visit_2'] = self.unreached_after_visits_qs(2).count()
        absentee_strat['visit_3'] = self.unreached_after_visits_qs(3).count()
        return absentee_strat

    def first_time_testers_qs(self):
        return self.community_members.filter(subjectvisit__hivtestinghistory__has_tested='No')

    def age_eligible_qs(self):
        enrolled_ids = HouseholdReportQuery.enrolled_ids_qs(self.community)
        return self.community_members.filter(age_in_years__gte=16, household_structure__household_id__in=enrolled_ids)

    def tested_qs(self):
        return self.community_members.exclude(subjectvisit__hivtested=None)

    def study_eligible_qs(self):
        return SubjectConsent.objects.filter(household_member__household_structure__household__community=self.community).count()

    def reached_stats(self):
        return self._residents_demographics('REFUSED', 'UNDECIDED', 'RESEARCH')

    def absentee_qs(self):
        return self.community_members.filter(member_status='ABSENT')

    def enrolled_stats(self):
        return self._residents_demographics('RESEARCH')

    def _residents_demographics(self, *args):
        demographics = {}
        demo_query = self.community_members.filter(member_status__in=args)
        demographics['count'] = demo_query.count()
        demographics['males'] = demo_query.filter(gender='M').count()
        demographics['females'] = demo_query.filter(gender='F').count()
        age_ranges = [(16, 19), (20, 29), (30, 39), (40, 49), (50, 79)]
        groups = {}
        for(a, b) in age_ranges:
            groups["{0}-{1}".format(a, b)] = demo_query.filter(age_in_years__range=(a, b)).count()
        demographics['age_groups'] = groups
        return demographics

    def unreached_after_visits_qs(self, no_of_visits):
        absentee_count_query = self.absentee_qs().annotate(absentee_count=Count('subjectabsentee__subjectabsenteeentry'))
        return absentee_count_query.filter(absentee_count=no_of_visits)

    def self_reported_stats(self):
        stat = dict(count=self.self_reported_infected)
        stat['on_arv'] = self.on_ART(self.self_reported_positive_qs()).count()
        stat['not_on_arv'] = self.not_on_ART(self.self_reported_positive_qs()).count()
        return stat

    def documented_positive_stats(self):
        stat = dict(count=self.already_infected)
        stat['on_arv'] = self.on_ART(self.already_infected_qs()).count()
        stat['not_on_arv'] = self.not_on_ART(self.already_infected_qs()).count()
        return stat

    def hiv_positive_qs(self):
        return self.community_members.filter(subjectvisit__hivresult__hiv_result='POS')

    def new_infections_qs(self):
        untested_Q = Q(subjectvisit__hivtestinghistory__has_tested='No')
        tested_Q = Q(subjectvisit__hivtestinghistory__verbal_hiv_result__in=['NEG', 'UNK', 'IND'])
        return self.hiv_positive_qs().filter(untested_Q | tested_Q)

    def already_infected_qs(self):
        review_Q = Q(subjectvisit__hivtestreview__recorded_hiv_result='POS')
        document_Q = Q(subjectvisit__hivresultdocumentation__result_recorded='POS')
        return self.hiv_positive_qs().filter(review_Q | document_Q)

    def self_reported_positive_qs(self):
        return self.hiv_positive_qs().filter(subjectvisit__hivtestinghistory__verbal_hiv_result='POS')

    def on_ART(self, hiv_positive_qs):
        return hiv_positive_qs.filter(subjectvisit__hivcareadherence__on_arv='Yes')

    def not_on_ART(self, hiv_positive_qs):
        return hiv_positive_qs.filter(subjectvisit__hivcareadherence__on_arv='No')