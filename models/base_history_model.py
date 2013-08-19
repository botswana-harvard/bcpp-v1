from django.db import models
from bhp_sync.models import BaseSyncUuidModel


class BaseHistoryModel(BaseSyncUuidModel):

    subject_identifier = models.CharField(max_length=25, db_index=True)
    report_datetime = models.DateTimeField(null=True, db_index=True)
    group_name = models.CharField(max_length=25)
    test_code = models.CharField(max_length=25)
    value = models.CharField(max_length=25)
    value_datetime = models.DateTimeField()
    source_model_name = models.CharField(max_length=50)
    source_app_label = models.CharField(max_length=50, null=True, blank=False)
    source_identifier = models.CharField(max_length=50, null=True)
    history_datetime = models.DateTimeField(null=True)

    def __unicode__(self):
        return '{0}-{1}-{2}-{3}-{4}'.format(self.subject_identifier, self.test_code, self.value, self.value_datetime, self.pk)

    class Meta:
        abstract = True
