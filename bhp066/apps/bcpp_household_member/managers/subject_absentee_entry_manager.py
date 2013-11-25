from datetime import timedelta
from django.db import models


class SubjectAbsenteeEntryManager(models.Manager):
    def get_by_natural_key(self, report_datetime, household_identifier, survey_name, subject_identifier_as_pk):
        margin = timedelta(microseconds=999)
        SubjectAbsentee = models.get_model('bcpp_household_member', 'SubjectAbsentee')
        subject_absentee = SubjectAbsentee.objects.get_by_natural_key(household_identifier, survey_name, subject_identifier_as_pk)
        return self.get(report_datetime__range=(report_datetime - margin, report_datetime + margin),
                        subject_absentee=subject_absentee)