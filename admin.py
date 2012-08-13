from django.contrib import admin
#from bhp_export_data.actions import export_as_csv_action
from bhp_base_model.classes import BaseModelAdmin
from models import GradingList, GradingListItem, ReferenceRangeList, ReferenceRangeListItem


class GradingListAdmin(BaseModelAdmin):
    pass
admin.site.register(GradingList, GradingListAdmin)


class GradingListItemAdmin(BaseModelAdmin):
    list_display = ('test_code', 'gender', 'hiv_status', 'grade', 'lln', 'uln', 'age_low', 'age_low_unit', 'age_low_quantifier',
                    'age_high', 'age_high_unit', 'age_high_quantifier', 'grading_list')
    search_fields = ['grade', 'test_code__code', 'test_code__name', 'lln', 'uln', 'hiv_status']
admin.site.register(GradingListItem, GradingListItemAdmin)


class ReferenceRangeListAdmin(BaseModelAdmin):
    pass
admin.site.register(ReferenceRangeList, ReferenceRangeListAdmin)


class ReferenceRangeListItemAdmin(BaseModelAdmin):
    pass
admin.site.register(ReferenceRangeListItem, ReferenceRangeListItemAdmin)
