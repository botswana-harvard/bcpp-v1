from django.db import models

from edc_lab.lab_packing.models import BasePackingListItem
from edc_sync.model_mixins import SyncModelMixin
from edc_base.model.models import BaseUuidModel

from .aliquot import Aliquot
from .packing_list import PackingList
from .panel import Panel
from .subject_requisition import SubjectRequisition
from .receive import Receive

from ..managers import PackingListItemManager


class PackingListItem(BasePackingListItem, SyncModelMixin, BaseUuidModel):

    packing_list = models.ForeignKey(PackingList, null=True)

    panel = models.ForeignKey(
        Panel,
        null=True,
        blank=True,
    )

    objects = PackingListItemManager()

    def save(self, *args, **kwargs):
        try:
            self.panel = self.subject_requisition.panel
            self.item_datetime = self.subject_requisition.drawn_datetime
        except AttributeError:
            pass
        super(PackingListItem, self).save(*args, **kwargs)

    @property
    def subject_requisition(self):
        """Returns the SubjectRequisition either directly or via the
        Aliquot."""
        try:
            return SubjectRequisition.objects.get(specimen_identifier=self.item_reference)
        except SubjectRequisition.DoesNotExist:
            aliquot = Aliquot.objects.get(aliquot_identifier=self.item_reference)
            return SubjectRequisition.objects.get(
                requisition_identifier=aliquot.receive.requisition_identifier)

    @property
    def receive(self):
        """Returns an instance of Receive using the requisition_identifier or None."""
        try:
            return Receive.objects.get(requisition_identifier=self.subject_requisition.requisition_identifier)
        except Receive.DoesNotExist:
            return None

    @property
    def drawn_datetime(self):
        """Returns the sample datetime drawn from the SubjectRequisition."""
        try:
            return self.subject_requisition.drawn_datetime
        except AttributeError:
            return '?'

    def clinician(self):
        try:
            return self.subject_requisition.user_created
        except AttributeError:
            return '?'

    def gender(self):
        try:
            return self.subject_requisition.registered_subject.gender
        except AttributeError:
            return '?'

    def natural_key(self):
        return (self.item_reference, )

    class Meta:
        app_label = "bcpp_lab"
        verbose_name = 'Packing List Item'
        ordering = ('-created', )
