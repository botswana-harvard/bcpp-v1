from django.contrib import admin
from edc_core.bhp_base_admin.admin import BaseModelAdmin
from bcpp_household.models import Community


class CommunityAdmin(BaseModelAdmin):
    pass

admin.site.register(Community, CommunityAdmin)
