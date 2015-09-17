from datetime import datetime

from django.db import models
from django_extensions.db.fields import UUIDField

from edc.base.model.fields import OtherCharField

from edc.base.model.models import BaseUuidModel

from bhp066.apps.bcpp.choices import WHYNOPARTICIPATE_CHOICE
from bhp066.apps.bcpp_survey.models import Survey

from ..managers import SubjectRefusalHistoryManager

from .household_member import HouseholdMember


class SubjectRefusalHistory(BaseUuidModel):
    """A system model that tracks the history of deleted refusal instances."""

    transaction = UUIDField()

    household_member = models.ForeignKey(HouseholdMember)

    report_datetime = models.DateTimeField(
        verbose_name="Report date",
        default=datetime.today())

    survey = models.ForeignKey(Survey, editable=False)

    refusal_date = models.DateField(
        verbose_name="Date subject refused participation",
        help_text="Date format is YYYY-MM-DD")

    reason = models.CharField(
        verbose_name=("We respect your decision to decline. It would help us"
                      " improve the study if you could tell us the main reason"
                      " you do not want to participate in this study?"),
        max_length=50,
        choices=WHYNOPARTICIPATE_CHOICE,
        help_text="",
    )
    reason_other = OtherCharField()

    objects = SubjectRefusalHistoryManager()

    def natural_key(self):
        return (self.transaction, )

    def get_report_datetime(self):
        return self.report_datetime

    def get_registration_datetime(self):
        return self.report_datetime

    class Meta:
        app_label = 'bcpp_household_member'
        verbose_name = 'Subject Refusal History'
