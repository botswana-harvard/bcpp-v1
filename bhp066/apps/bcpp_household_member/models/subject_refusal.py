from django.db import models
from django.utils.translation import ugettext_lazy as _

from edc.audit.audit_trail import AuditTrail
from edc.base.model.fields import OtherCharField
from edc.base.model.validators import date_not_future, date_not_before_study_start

from apps.bcpp.choices import WHYNOPARTICIPATE_CHOICE
from apps.bcpp_household_member.constants import REFUSED
from apps.bcpp_household_member.exceptions import MemberStatusError

from apps.bcpp_household.exceptions import AlreadyReplaced
from apps.bcpp_household_member.classes import HouseholdMemberHelper

from .base_member_status_model import BaseMemberStatusModel


class SubjectRefusal (BaseMemberStatusModel):

    refusal_date = models.DateField(
        verbose_name=_("Date subject refused participation"),
        validators=[date_not_before_study_start, date_not_future],
        help_text="Date format is YYYY-MM-DD")

    reason = models.CharField(
        verbose_name=_("We respect your decision to decline. It would help us"
                       " improve the study if you could tell us the main reason"
                       " you do not want to participate in this study?"),
        max_length=50,
        choices=WHYNOPARTICIPATE_CHOICE,
        help_text="")

    reason_other = OtherCharField()

    subject_refusal_status = models.CharField(
        verbose_name=_("Refusal status"),
        max_length=100,
        help_text=_("Change the refusal status from 'refused' to 'no longer refusing' if and"
                    " when the subject changes their mind"),
        default='REFUSED',
        editable=False)

    comment = models.CharField(
        verbose_name=_("Comment"),
        max_length=250,
        null=True,
        blank=True,
        help_text=_('IMPORTANT: Do not include any names or other personally identifying '
                    'information in this comment'))

    history = AuditTrail()

    def get_registration_datetime(self):
        return self.report_datetime

    def save(self, *args, **kwargs):
        household = models.get_model('bcpp_household', 'Household').objects.get(household_identifier=self.household_member.household_structure.household.household_identifier)
        if household.replaced_by:
            raise AlreadyReplaced('Household {0} replaced.'.format(household.household_identifier))
#         if self.household_member.member_status != REFUSED:
#             raise MemberStatusError('Expected member status to be {0}. Got {1}'.format(REFUSED, self.household_member.member_status))
#         if self.household_member.enrollment_checklist_completed and not self.household_member.eligible_subject:
#             raise MemberStatusError('The Enrollment Checklist has been filled and subject is not eligible for BHS. Refusal form is not required')
        self.survey = self.household_member.survey
        self.registered_subject = self.household_member.registered_subject
        self.household_member.refused = True
        #household_member_helper = HouseholdMemberHelper(self.household_member)
        #self.household_member.member_status = household_member_helper.calculate_member_status_without_hint()
        self.household_member.member_status = REFUSED
        # important during dispatch, need to save instance to the correct db.
        self.household_member.save(using=kwargs.get('using', None))
        super(SubjectRefusal, self).save(*args, **kwargs)

    class Meta:
        app_label = "bcpp_household_member"
        verbose_name = "Subject Refusal"
        verbose_name_plural = "Subject Refusal"
        ordering = ['household_member']
