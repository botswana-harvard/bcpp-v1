from django.contrib import admin

from ..forms import ViralLoadResultForm
from ..models import ViralLoadResult

from .subject_visit_model_admin import SubjectVisitModelAdmin


class ViralLoadResultAdmin(SubjectVisitModelAdmin):

    form = ViralLoadResultForm
    list_display = ('subject_visit', 'sample_id', 'clinician_initials',
                    'collection_datetime', 'result_value', 'clinic', 'assay_performed_by', 'validated_by')
    list_filter = ('clinician_initials', 'collection_datetime', 'report_datetime',
                   'result_value', 'clinic__site_name', )
    search_fields = ('subject_visit', 'sample_id', 'clinician_initials',
                     'collection_datetime', 'result_value', 'clinic', )

admin.site.register(ViralLoadResult, ViralLoadResultAdmin)