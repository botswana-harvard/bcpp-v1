from edc_base.audit_trail import AuditTrail

from .detailed_sexual_history import DetailedSexualHistory


class SecondPartner (DetailedSexualHistory):

    history = HistoricalRecords()

    class Meta(CrfModelMixin.Meta):
        app_label = 'bcpp_subject'
        verbose_name = "CS003: Second Partner"
        verbose_name_plural = "CS003: Second Partner"
