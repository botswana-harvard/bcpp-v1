from django.db import models
from edc.device.inspector.models import BaseInspector


class SubjectRequisitionInspector(BaseInspector):

    subject_identifier = models.CharField(
        max_length=25,
        verbose_name='Subject Identifier'
        )

    requisition_datetime = models.DateTimeField(
        verbose_name='Requisition Date'
        )

    requisition_identifier = models.CharField(
        max_length=50,
        verbose_name='Requisition Identifier'
        )

    aliquot_type = models.CharField(
        max_length=10,
        verbose_name='Aliquot Type'
        )

    specimen_identifier = models.CharField(
        max_length=50,
        verbose_name='Specimen Identifier'
        )

    device_id = models.CharField(
        max_length=15,
        verbose_name='Device Id'
        )

    class Meta:
        app_label = 'bcpp_inspector'
        verbose_name = 'Subject Requisition Inspector'
