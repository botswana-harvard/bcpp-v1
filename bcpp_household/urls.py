from django.conf.urls import url

from .admin_site import bcpp_household_admin

urlpatterns = [
    url(r'^admin/', bcpp_household_admin.urls),
]
