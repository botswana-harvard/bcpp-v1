from django.contrib import admin
from bhp_base_admin.admin import BaseModelAdmin
from bcpp_household.models import GpsDevice


class GpsDeviceAdmin(BaseModelAdmin):
    pass

admin.site.register(GpsDevice, GpsDeviceAdmin)
