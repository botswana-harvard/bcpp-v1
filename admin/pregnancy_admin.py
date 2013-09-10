from django.contrib import admin
from subject_visit_model_admin import SubjectVisitModelAdmin
from bcpp_subject.models import Pregnancy
from bcpp_subject.forms import PregnancyForm


class PregnancyAdmin(SubjectVisitModelAdmin):

    form = PregnancyForm
    fields = (
        "subject_visit",
        'anc_reg',
        'lnmp',
        'last_birth',
        'anc_last_pregnancy',
        'hiv_last_pregnancy',
        'preg_arv',)
    radio_fields = {
        "anc_reg": admin.VERTICAL,
        "anc_last_pregnancy": admin.VERTICAL,
        "hiv_last_pregnancy": admin.VERTICAL,
        "preg_arv": admin.VERTICAL, }
admin.site.register(Pregnancy, PregnancyAdmin)
