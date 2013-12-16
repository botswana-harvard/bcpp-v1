from apps.bcpp_household.models.plot import Plot
from django.db.models import Count, Sum


class PlotReportQuery(object):
    def __init__(self, community):
        self.community = community
        self.plots = Plot.objects.filter(community=community)
        self.targeted = self.targeted_qs().count()
        self.household_count = self.plot_stats().get('household_count')
        self.verified_residential = self.plot_stats().get('verified_count')

    def targeted_qs(self):
        return self.plots.exclude(selected=None)

    def confirmed_occupied_qs(self):
        return self.targeted_qs().filter(action='confirmed', status__istartswith='occupied')

    def plot_stats(self):
        return self.confirmed_occupied_qs().aggregate(household_count=Sum('household_count'), verified_count=Count('pk'))
