from django.contrib import admin
from django.utils.translation import ugettext as _

from ..forms import ReproductiveHealthForm
from ..models import ReproductiveHealth

from .subject_admin_exclude_mixin import SubjectAdminExcludeMixin
from .subject_visit_model_admin import SubjectVisitModelAdmin


class ReproductiveHealthAdmin(SubjectAdminExcludeMixin, SubjectVisitModelAdmin):

    form = ReproductiveHealthForm
    fields = [
        "subject_visit",
        "number_children",
        "menopause",
        "family_planning",
        "family_planning_other",
        'currently_pregnant',
        'when_pregnant',
        'gestational_weeks',
        'pregnancy_hiv_tested',
        'pregnancy_hiv_retested']

    custom_exclude = {'baseline': [
        "when_pregnant",
        "gestational_weeks",
        "pregnancy_hiv_tested",
        "pregnancy_hiv_retested"]
    }

    radio_fields = {
        "menopause": admin.VERTICAL,
        "currently_pregnant": admin.VERTICAL,
        "when_pregnant": admin.VERTICAL,
        "pregnancy_hiv_tested": admin.VERTICAL,
        "pregnancy_hiv_retested": admin.VERTICAL
    }

    filter_horizontal = ("family_planning",)
    instructions = [("<h5>Note to Interviewer</h5> This section is to be"
                     " completed by female participants. SKIP for male participants."),
                    _("Read to Participant: I am now going to ask you questions"
                      " about reproductive health and pregnancy.")]

admin.site.register(ReproductiveHealth, ReproductiveHealthAdmin)
