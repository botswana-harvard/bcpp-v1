from django.db import models

from edc.audit.audit_trail import AuditTrail
from edc.base.model.fields import InitialsField
from edc.core.bhp_variables.models import StudySite
from edc.core.crypto_fields.fields import EncryptedCharField
from edc.core.crypto_fields.fields import EncryptedTextField
from edc.entry_meta_data.managers import EntryMetaDataManager

from .base_clinic_visit_model import BaseClinicVisitModel
from .clinic_visit import ClinicVisit


class ClinicVlResult(BaseClinicVisitModel):
    """A model completed by the user that captures the viral load result associated with the RBD."""
    site = models.ForeignKey(StudySite)

    clinician_initials = InitialsField(
        verbose_name='Clinician initial',
        default='--',
    )

    collection_datetime = models.DateTimeField(
        verbose_name='The datetime sample was drawn',
        help_text='',
    )

    assay_date = models.DateField(
        verbose_name='Assay date',
        help_text='',
    )

    result_value = models.IntegerField(
        verbose_name="Result Value",
        help_text=("copies/ml"),)

    comment = EncryptedTextField(
        verbose_name="Comment",
        max_length=250,
        blank=True,
        null=True
    )

    validation_date = models.DateField(
        verbose_name='Date result was validated',
        help_text='',
    )

    validated_by = EncryptedCharField(
        max_length=35,
        verbose_name="Validated by",
    )

    history = AuditTrail()

    entry_meta_data_manager = EntryMetaDataManager(ClinicVisit)

    class Meta:
        app_label = "bcpp_clinic"
        verbose_name = "Clinic VL Result"
        verbose_name_plural = "Clinic VL Result"
