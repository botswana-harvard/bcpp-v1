from django.db import models
from django.utils.translation import ugettext as _

from edc.audit.audit_trail import AuditTrail
from edc.base.model.fields import OtherCharField
from edc.base.model.validators import date_not_future
from edc.entry_meta_data.managers import EntryMetaDataManager

from apps.bcpp.choices import (YES_NO_DWTA, YES_NO, WHYNOARV_CHOICE, ADHERENCE4DAY_CHOICE,
                               ADHERENCE4WK_CHOICE, NO_MEDICAL_CARE, WHYARVSTOP_CHOICE)

from .subject_visit import SubjectVisit
from .base_scheduled_visit_model import BaseScheduledVisitModel


class HivCareAdherence (BaseScheduledVisitModel):

    first_positive = models.DateField(
        verbose_name=_("When was your first positive HIV test result?"),
        validators=[date_not_future],
        null=True,
        blank=True,
        help_text=("Note: If participant does not want to answer, leave blank. "
                   "If participant is unable to estimate date, leave blank."),
        )

    medical_care = models.CharField(
        verbose_name=_("Have you ever received HIV-related medical or clinical"
                      " care, for such things as a CD4 count (masole), IDCC/ PMTCT"
                      " registration, additional clinic-based counseling?"),
        max_length=25,
        choices=YES_NO_DWTA,
        help_text="if 'YES', answer HIV medical care section",
        )

    no_medical_care = models.CharField(
        verbose_name=_("What is the main reason you have not received HIV-related"
                       " medical or clinical care?"),
        max_length=70,
        null=True,
        blank=True,
        choices=NO_MEDICAL_CARE,
        help_text="",
        )
    no_medical_care_other = OtherCharField()

    ever_recommended_arv = models.CharField(
        verbose_name=_("Have you ever been recommended by a doctor/nurse or other healthcare "
                        "worker to start antiretroviral therapy (ARVs), a combination of medicines "
                        "to treat your HIV infection? [common medicines include: combivir, truvada, "
                        "atripla, nevirapine]"),
        max_length=25,
        choices=YES_NO_DWTA,
        null=True,
        blank=True,
        help_text="",
        )

    arv_naive = models.CharField(
        verbose_name=_("Have you ever taken any antiretroviral therapy (ARVs) for your HIV infection?"
                        " [For women: Do not include treatment that you took during pregnancy to protect "
                        "your baby from HIV]"),
        max_length=25,
        choices=YES_NO_DWTA,
        help_text="",
        )

    why_no_arv = models.CharField(
        verbose_name=_("What was the main reason why you have not started ARVs?"),
        max_length=75,
        null=True,
        blank=True,
        choices=WHYNOARV_CHOICE,
        help_text="",
        )
    why_no_arv_other = OtherCharField()

    first_arv = models.DateField(
        verbose_name=_("When did you first start taking antiretroviral therapy (ARVs)?"),
        validators=[date_not_future],
        null=True,
        blank=True,
        help_text=("Note: If participant does not want to answer,leave blank.  "
                   "If participant is unable to estimate date, leave blank."),
        )

    on_arv = models.CharField(
        verbose_name=_("Are you currently taking antiretroviral therapy (ARVs)?"),
        max_length=25,
        choices=YES_NO_DWTA,
        help_text="If yes, need to answer next two questions.",
        )

    clinic_receiving_from = models.CharField(
        verbose_name=_('Which clinic facility are you already receiving therapy from?'),
        default=None,
        null=True,
        max_length=50,
        help_text=""
        )

    next_appointment_date = models.DateField(
         verbose_name=_("When is your next appointment at this facility?"),
         default=None,
         null=True,
         help_text=""
         )

    arv_stop_date = models.DateField(
        verbose_name=_("When did you stop taking ARV\'s?"),
        validators=[date_not_future],
        null=True,
        blank=True,
        help_text="",
        )

    arv_stop = models.CharField(
        verbose_name=_("What was the main reason why you stopped taking ARVs?"),
        max_length=80,
        choices=WHYARVSTOP_CHOICE,
        null=True,
        blank=True,
        help_text="",
        )

    arv_stop_other = OtherCharField()

    adherence_4_day = models.CharField(
        verbose_name=_("During the past 4 days, on how many days have you missed taking all your"
                        " doses of antiretroviral therapy (ART)?"),
        max_length=25,
        choices=ADHERENCE4DAY_CHOICE,
        null=True,
        blank=True,
        help_text="",
        )

    adherence_4_wk = models.CharField(
        verbose_name=_("Thinking about the past 4 weeks, on average, how would you rate your "
                        "ability to take all your medications as prescribed?"),
        max_length=25,
        null=True,
        blank=True,
        choices=ADHERENCE4WK_CHOICE,
        help_text="",
        )

    arv_evidence = models.CharField(
        verbose_name=_("Is there evidence [OPD card, tablets, masa number] that the participant is on therapy?"),
        choices=YES_NO,
        null=True,
        blank=True,
        max_length=3,
        )

    history = AuditTrail()

    entry_meta_data_manager = EntryMetaDataManager(SubjectVisit)

    def defaulter(self):
        """Returns true if subject is an ARV defaulter."""
        if self.arv_evidence == 'Yes' and self.on_arv == 'No':
            return True
        return None

    def on_art(self):
        if self.on_arv == 'Yes':
            return True
        elif self.on_arv == 'No':
            if self.arv_evidence == 'Yes':
                return True  # defaulter
            return False
        else:
            return None

    def get_clinic_receiving_from(self):
        return self.clinic_receiving_from

    def get_next_appointment_date(self):
        return self.next_appointment_date

    class Meta:
        app_label = 'bcpp_subject'
        verbose_name = "HIV care & Adherence"
        verbose_name_plural = "HIV care & Adherence"
