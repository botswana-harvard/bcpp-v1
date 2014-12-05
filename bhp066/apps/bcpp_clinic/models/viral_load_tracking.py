from django.db import models

from edc.audit.audit_trail import AuditTrail
from edc.base.model.fields import InitialsField
from edc.choices.common import YES_NO
from edc.entry_meta_data.managers import EntryMetaDataManager
from edc.lab.lab_requisition.choices import REASON_NOT_DRAWN

from .base_clinic_visit_model import BaseClinicVisitModel
from .clinic_visit import ClinicVisit


class ViralLoadTracking(BaseClinicVisitModel):

    is_drawn = models.CharField(
        verbose_name='Was a specimen drawn?',
        max_length=3,
        choices=YES_NO,
        default='Yes',
        help_text='If No, provide a reason below'
        )

    reason_not_drawn = models.CharField(
        verbose_name='If not drawn, please explain',
        max_length=25,
        choices=REASON_NOT_DRAWN,
        null=True,
        blank=True,
        )

    drawn_datetime = models.DateTimeField(
        verbose_name='Date / Time Specimen Drawn',
        null=True,
        blank=True,
        help_text='If not drawn, leave blank. Same as date and time of finger prick in case on DBS.',
        )

    clinician_initials = InitialsField(
        verbose_name='Clinician\'s initial',
        null=True,
        blank=True,
        default='--',
        )

    history = AuditTrail()

    entry_meta_data_manager = EntryMetaDataManager(ClinicVisit)

    class Meta:
        app_label = 'bcpp_clinic'
        verbose_name = 'Viral Load Tracking'
        verbose_name_plural = 'Viral Load Tracking'
