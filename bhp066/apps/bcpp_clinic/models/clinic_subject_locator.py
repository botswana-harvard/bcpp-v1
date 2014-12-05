from django.db import models
from django.utils.translation import ugettext_lazy as _

from edc.audit.audit_trail import AuditTrail
from edc.base.model.validators import BWCellNumber, BWTelephoneNumber
from edc.choices.common import YES_NO
from edc.core.crypto_fields.fields import EncryptedCharField
from edc.entry_meta_data.managers import EntryMetaDataManager
from edc.export.managers import ExportHistoryManager
from edc.export.models import ExportTrackingFieldsMixin
from edc.subject.locator.models import BaseLocator

from ..managers import ClinicModelManager

from .clinic_off_study_mixin import ClinicOffStudyMixin
from .clinic_visit import ClinicVisit


class ClinicSubjectLocator(ExportTrackingFieldsMixin, ClinicOffStudyMixin, BaseLocator):
    """A model completed by the user for locator data from consented participants."""
    clinic_visit = models.ForeignKey(ClinicVisit)

    alt_contact_cell_number = EncryptedCharField(
        max_length=8,
        verbose_name=_("Cell number (alternate)"),
        validators=[BWCellNumber, ],
        help_text="",
        blank=True,
        null=True,
        )
    has_alt_contact = models.CharField(
        max_length=25,
        choices=YES_NO,
        verbose_name=_("If we are unable to contact the person indicated above, is there another"
                       " individual (including next of kin) with whom the study team can get"
                       " in contact with?"),
        help_text="",
        )

    alt_contact_name = EncryptedCharField(
        max_length=35,
        verbose_name=_("Full Name of the responsible person"),
        help_text="include first name and surname",
        blank=True,
        null=True,
        )

    alt_contact_rel = EncryptedCharField(
        max_length=35,
        verbose_name=_("Relationship to participant"),
        blank=True,
        null=True,
        help_text="",
        )
    alt_contact_cell = EncryptedCharField(
        max_length=8,
        verbose_name=_("Cell number"),
        validators=[BWCellNumber, ],
        help_text="",
        blank=True,
        null=True,
        )

    other_alt_contact_cell = EncryptedCharField(
        max_length=8,
        verbose_name=_("Cell number (alternate)"),
        validators=[BWCellNumber, ],
        help_text="",
        blank=True,
        null=True,
        )

    alt_contact_tel = EncryptedCharField(
        max_length=8,
        verbose_name=_("Telephone number"),
        validators=[BWTelephoneNumber, ],
        help_text="",
        blank=True,
        null=True,
        )

    export_history = ExportHistoryManager()

    history = AuditTrail()

    entry_meta_data_manager = EntryMetaDataManager(ClinicVisit)

    objects = ClinicModelManager()

    def save(self, *args, **kwargs):
        if self.clinic_visit:
            if not self.registered_subject:
                self.registered_subject = self.clinic_visit.appointment.registered_subject
        super(ClinicSubjectLocator, self).save(*args, **kwargs)

    def natural_key(self):
        return self.clinic_visit.natural_key()

    def get_visit(self):
        return self.clinic_visit

    def get_subject_identifier(self):
        if self.get_visit():
            return self.get_visit().get_subject_identifier()
        return None

    def get_report_datetime(self):
        return self.created

    def __unicode__(self):
        return unicode(self.clinic_visit)

    class Meta:
        app_label = 'bcpp_clinic'
        verbose_name = "Clinic Subject Locator"
        verbose_name_plural = "Clinic Subject Locator"