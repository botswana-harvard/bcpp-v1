from django.contrib import admin

from ..forms import ResourceUtilizationForm
from ..models import ResourceUtilization

from .subject_visit_model_admin import SubjectVisitModelAdmin


class ResourceUtilizationAdmin(SubjectVisitModelAdmin):

    form = ResourceUtilizationForm
    fields = (
        "subject_visit",
        "out_patient",
        "hospitalized",
        "money_spent",
        "medical_cover",
    )
    radio_fields = {
        "out_patient": admin.VERTICAL,
        "medical_cover": admin.VERTICAL,
    }
    instructions = [
        ("<H5>Note to Interviewer</H5> Complete this interview with the participant and enter "
         "the participant's response for each question. Each question is to be answered by "
         "the participant, not the interviewer. Please check only one box for each question."),
        ("<H5>Read to Participant:</H5> Next, I will ask questions about health care visits over "
         "the past three months. Please think about all visits for any health issue, "
         "including pregnancy.")]
admin.site.register(ResourceUtilization, ResourceUtilizationAdmin)
