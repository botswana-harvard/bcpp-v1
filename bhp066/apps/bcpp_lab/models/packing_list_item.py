from django.db import models

from edc.subject.registration.models import RegisteredSubject
from edc.lab.lab_packing.models import BasePackingListItem

from .aliquot import Aliquot
from .packing_list import PackingList
from .panel import Panel
from .subject_requisition import SubjectRequisition


class PackingListItem(BasePackingListItem):

    packing_list = models.ForeignKey(PackingList, null=True)

    panel = models.ForeignKey(Panel,
        null=True,
        blank=True,
        )

    def drawn_datetime(self):
        retval = "n/a"
        if self.item_reference:
            aliquot = Aliquot.objects.get(aliquot_identifier=self.item_reference)
            requisition = SubjectRequisition.objects.get(
                                requisition_identifier=aliquot.receive.requisition_identifier
                                )
            retval = requisition.drawn_datetime
        return retval

    def clinician(self):
        retval = "n/a"
        if self.item_reference:
            aliquot = Aliquot.objects.get(aliquot_identifier=self.item_reference)
            requisition = SubjectRequisition.objects.get(
                                requisition_identifier=aliquot.receive.requisition_identifier
                                )
            retval = requisition.user_created
        return retval

    def gender(self):
        retval = "n/a"
        if self.item_reference:
            aliquot = Aliquot.objects.get(aliquot_identifier=self.item_reference)
            requisition = SubjectRequisition.objects.get(
                                requisition_identifier=aliquot.receive.requisition_identifier
                                )
            subject_identifier = requisition.subject()
            if subject_identifier:
                registered_subject = RegisteredSubject.objects.get(
                                        subject_identifier=subject_identifier
                                    )
                retval = registered_subject.gender
        return retval

    class Meta:
        app_label = "bcpp_lab"
        verbose_name = 'Packing List Item'
