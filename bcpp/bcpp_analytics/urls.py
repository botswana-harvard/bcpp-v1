from django.conf.urls import patterns, url
from .views import (index, operational_report_plots_view, operational_report_view,
                    replacement_report_view, accrual, accrual_pdf, key_indicators,
                    key_indicators_pdf, operational_report_household_view,
                    operational_report_member_view, operational_report_specimen_view,
                    operational_report_annual_view, operational_report_rbd_view,
                    operational_report_visits_view, operational_report_consents_view)

urlpatterns = patterns(
    '',
    url(r'^reports/$', index, name="index"),
    url(r'^report/community_accrual/$', accrual, name="accrual"),
    url(r'^report/community_accrual/pdf/(?P<com1>\w+)'
        '/(?P<com2>\w+)/(?P<start>[a-zA-Z0-9_., ]+)/(?P<to>[a-zA-Z0-9_., ]+)/$',
        accrual_pdf, name="accrual_pdf"),
    url(r'^report/operational/$', operational_report_view, name="operational"),
    url(r'^report/operational_plot/', operational_report_plots_view, name="operational_plot"),
    url(r'^report/operational_household/', operational_report_household_view, name="operational_household"),
    url(r'^report/operational_member/', operational_report_member_view, name="operational_member"),
    url(r'^report/operational_specimen/', operational_report_specimen_view, name="operational_specimen"),
    url(r'^report/operational_annual/', operational_report_annual_view, name="operational_annual"),
    url(r'^report/operational_rbd/', operational_report_rbd_view, name="operational_rbd"),
    url(r'^report/operational_visits/', operational_report_visits_view, name="operational_visits"),
    url(r'^report/operational_consents/', operational_report_consents_view, name="operational_consents"),
    url(r'^report/replacement/$', replacement_report_view, name="replacement"),
    url(r'^report/key_indicators/$', key_indicators, name="indicators"),
    url(r'^report/key_indicators/pdf/(?P<com1>\w+)/(?P<com2>\w+)'
        '/(?P<start>[a-zA-Z0-9_., ]+)/(?P<to>[a-zA-Z0-9_., ]+)/$',
        key_indicators_pdf, name="indicators_pdf"),
)
