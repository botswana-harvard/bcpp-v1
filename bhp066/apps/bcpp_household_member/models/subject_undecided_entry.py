from django.db import models

from edc.audit.audit_trail import AuditTrail

from apps.bcpp_household.exceptions import AlreadyReplaced
from apps.bcpp_household_member.classes import HouseholdMemberHelper

from ..choices import UNDECIDED_REASON
from ..managers import SubjectUndecidedEntryManager

from .base_subject_entry import BaseSubjectEntry
from .subject_undecided import SubjectUndecided


class SubjectUndecidedEntry(BaseSubjectEntry):

    subject_undecided = models.ForeignKey(SubjectUndecided)

    subject_undecided_reason = models.CharField(
        verbose_name="Reason",
        max_length=100,
        choices=UNDECIDED_REASON)

    history = AuditTrail()

    objects = SubjectUndecidedEntryManager()

    def save(self, *args, **kwargs):
        if self.subject_undecided.household_member.household_structure.household.replaced_by:
            raise AlreadyReplaced('Model {0}-{1} has its container replaced.'.format(self._meta.object_name, self.pk))
        household_member_helper = HouseholdMemberHelper(self.subject_undecided.household_member)
        if not self.id:
            household_member = self.subject_undecided.household_member
            household_member.visit_attempts += 1
            household_member.member_status = household_member_helper.calculate_member_status_without_hint()
            household_member.save()
        super(SubjectUndecidedEntry, self).save(*args, **kwargs)

    @property
    def inline_parent(self):
        return self.subject_undecided

    def natural_key(self):
        return (self.report_datetime,) + self.subject_undecided.natural_key()
    natural_key.dependencies = ['bcpp_subject.subjectundecided']

    class Meta:
        app_label = 'bcpp_household_member'
        verbose_name = "Subject Undecided Entry"
        verbose_name_plural = "Subject Undecided Entries"
        unique_together = ('subject_undecided', 'report_datetime')
