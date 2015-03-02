from datetime import timedelta

from django.db import models


class GrantManager(models.Manager):

    def get_by_natural_key(
            self, report_datetime, visit_report_datetime, visit_instance, code, subject_identifier_as_pk):
        margin = timedelta(microseconds=999)
        LabourMarketWages = models.get_model('bcpp_subject', 'LabourMarketWages')
        labour_market_wages = LabourMarketWages.objects.get_by_natural_key(
            visit_report_datetime, visit_instance, code, subject_identifier_as_pk)
        return self.get(report_datetime__range=(report_datetime - margin, report_datetime + margin),
                        labour_market_wages=labour_market_wages)
