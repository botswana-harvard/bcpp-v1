from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _

#from ..models import SubjectReferral, ClinicSubjectLocator
from ..models import ClinicSubjectLocator


class ClinicSubjectLocatorIsReferredListFilter(SimpleListFilter):

    title = _('referred')

    parameter_name = 'referred'

    def lookups(self, request, model_admin):
        return ((True, 'Yes'), (False, 'No'), )

#     def queryset(self, request, queryset):
#         locators = []
#         if self.value():
#             for qs in queryset:
#                 if SubjectReferral.objects.filter(subject_visit__appointment__registered_subject__subject_identifier=qs.get_subject_identifier()).exclude(referral_code__in=['NOT-REF', 'ERROR']):
#                     locators.append(qs.get_subject_identifier())
#             queryset = ClinicSubjectLocator.objects.filter(subject_visit__appointment__registered_subject__subject_identifier__in=locators)
#         if self.value() == False:
#             for qs in queryset:
#                 if SubjectReferral.objects.filter(subject_visit__appointment__registered_subject__subject_identifier=qs.get_subject_identifier(), referral_code__in=['NOT-REF', 'ERROR']):
#                     locators.append(qs.get_subject_identifier())
#             queryset = ClinicSubjectLocator.objects.filter(subject_visit__appointment__registered_subject__subject_identifier__in=locators)
#         return queryset