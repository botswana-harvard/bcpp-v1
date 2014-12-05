from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _
from django.db.models import Count


class ClinicCommunityListFilter(SimpleListFilter):

    title = _('community')

    parameter_name = 'community'

    def lookups(self, request, model_admin):
        community_tuples = []
        for item in model_admin.model.objects.values(
                'clinic_visit__household_member__household_structure__household__plot__community'
                ).annotate(Count('clinic_visit__household_member__household_structure__household__plot__community')):
            for item in item['clinic_visit__household_member__household_structure__household__plot__community']:
                community_tuples.append((item, item))
        return tuple(community_tuples)

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                clinic_visit__household_member__household_structure__household__plot__community=self.value())