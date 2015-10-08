from django.contrib import admin

from ..models import (HivMedicalCare, HeartAttack, Cancer, Sti,
                      Tubercolosis, SubstanceUse)
from ..forms import (HivMedicalCareForm,
                     HeartAttackForm, CancerForm, StiForm,
                     TubercolosisForm, SubstanceUseForm)
from .subject_visit_model_admin import SubjectVisitModelAdmin


class HivMedicalCareAdmin(SubjectVisitModelAdmin):

    form = HivMedicalCareForm
    fields = (
        "subject_visit",
        "first_hiv_care_pos",
        "last_hiv_care_pos",
        'lowest_cd4',)
    radio_fields = {
        "lowest_cd4": admin.VERTICAL}
admin.site.register(HivMedicalCare, HivMedicalCareAdmin)


class HeartAttackAdmin(SubjectVisitModelAdmin):

    form = HeartAttackForm
    fields = (
        "subject_visit",
        "date_heart_attack",
        'dx_heart_attack',
        'dx_heart_attack_other',)
    filter_horizontal = ('dx_heart_attack',)
    instructions = [("Note to Interviewer: This form is to be filled for all participants"
                     " even if they do not have a record (on hand) of the diagnosis.")]
admin.site.register(HeartAttack, HeartAttackAdmin)


class CancerAdmin(SubjectVisitModelAdmin):

    form = CancerForm
    fields = (
        "subject_visit",
        "date_cancer",
        'dx_cancer',)
    radio_fields = {'dx_cancer': admin.VERTICAL, }
    instructions = [("Note to Interviewer: This form is to be filled for all participants"
                     " even if they do not have a record (on hand) of the diagnosis.")]
admin.site.register(Cancer, CancerAdmin)


class TubercolosisAdmin(SubjectVisitModelAdmin):

    form = TubercolosisForm
    fields = (
        "subject_visit",
        "date_tb",
        'dx_tb',
        'dx_tb_other')
    radio_fields = {
        "dx_tb": admin.VERTICAL, }
    instructions = [("Note to Interviewer: This form is to be filled for all participants"
                    " even if they do not have a record (on hand) of the diagnosis.")]
admin.site.register(Tubercolosis, TubercolosisAdmin)


class StiAdmin(SubjectVisitModelAdmin):

    form = StiForm
    fields = (
        "subject_visit",
        'sti_dx',
        'sti_dx_other',
        'wasting_date',
        'diarrhoea_date',
        'yeast_infection_date',
        'pneumonia_date',
        'pcp_date',
        'herpes_date',
        'comments',)
    filter_horizontal = ('sti_dx',)
admin.site.register(Sti, StiAdmin)


class SubstanceUseAdmin(SubjectVisitModelAdmin):

    form = SubstanceUseForm
    fields = (
        "subject_visit",
        'alcohol',
        'smoke',)
    radio_fields = {
        "alcohol": admin.VERTICAL,
        "smoke": admin.VERTICAL, }
    instructions = [("Read to Participant: I would like to now ask you "
                    "questions about drinking alcohol and smoking.")]
admin.site.register(SubstanceUse, SubstanceUseAdmin)
