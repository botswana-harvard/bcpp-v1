from django.db import models

from edc.audit.audit_trail import AuditTrail

from ..choices import ABSENTEE_REASON
from ..managers import SubjectAbsenteeEntryManager

from .base_subject_entry import BaseSubjectEntry
from .subject_absentee import SubjectAbsentee


class SubjectAbsenteeEntry(BaseSubjectEntry):

    subject_absentee = models.ForeignKey(SubjectAbsentee)

    reason = models.CharField(
        verbose_name="Reason?",
        max_length=100,
        choices=ABSENTEE_REASON,
        )

    history = AuditTrail()

    objects = SubjectAbsenteeEntryManager()

    def inline_parent(self):
        return self.subject_absentee

    def natural_key(self):
        return (self.report_datetime, ) + self.subject_absentee.natural_key()
    natural_key.dependencies = ['bcpp_subject.subjectabsentee', ]

    def save(self, *args, **kwargs):
        if self.__class__.objects.filter(subject_absentee=self.subject_absentee).count() == 2:
            household_member = self.subject_absentee.household_member
            household_member.member_status = 'ABSENTv3'
            household_member.save()
        super(SubjectAbsenteeEntry, self).save(*args, **kwargs)
        
    class Meta:
        app_label = 'bcpp_household_member'
        db_table = 'bcpp_subject_subjectabsenteeentry'
        verbose_name = "Subject Absentee Entry"
        verbose_name_plural = "Subject Absentee Entry"
        unique_together = ('subject_absentee', 'report_datetime')
