from django.contrib import admin
from htc_subject_visit_model_admin import HtcSubjectVisitModelAdmin
from bcpp_subject_htc.models import MaleFollowup
from bcpp_subject_htc.forms import MaleFollowupForm


class MaleFollowupAdmin(HtcSubjectVisitModelAdmin):

    form = MaleFollowupForm

    fields = (
      "contact_consent",
      "contact_family",
    )
    radio_fields = {
        "contact_consent": admin.VERTICAL,
        "contact_family": admin.VERTICAL,
        }
    instructions = [("For men who are HIV negative and uncircumcised")]
admin.site.register(MaleFollowup, MaleFollowupAdmin)
