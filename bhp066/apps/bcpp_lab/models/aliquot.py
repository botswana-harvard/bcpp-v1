from django.db import models
from django.core.urlresolvers import reverse

from lis.specimen.lab_aliquot.models import BaseAliquot

from apps.bcpp_subject.models import SubjectVisit

from ..managers import AliquotManager

from .aliquot_condition import AliquotCondition
from .aliquot_type import AliquotType
from .receive import Receive
from .subject_requisition import SubjectRequisition


class Aliquot(BaseAliquot):

    receive = models.ForeignKey(Receive,
        editable=False)

    aliquot_type = models.ForeignKey(AliquotType,
        verbose_name="Aliquot Type",
        null=True)

    aliquot_condition = models.ForeignKey(AliquotCondition,
        verbose_name="Aliquot Condition",
        null=True,
        blank=True)

    # community = models.CharField(max_length=25, choices=COMMUNITIES, null=True, editable=False)

    objects = AliquotManager()

    def save(self, *args, **kwargs):
        self.subject_identifier = self.receive.registered_subject.subject_identifier
        # self.community = site_mappers.current_mapper().map_area
        super(Aliquot, self).save(*args, **kwargs)

    @property
    def specimen_identifier(self):
        return self.aliquot_identifier[:-4]

    def get_visit_model(self):
        # from apps.bcpp_subject.models import SubjectVisit
        return SubjectVisit

    @property
    def registered_subject(self):
        return self.receive.registered_subject

    @property
    def visit_code(self):
        return self.receive.visit

    @property
    def subject_visit(self):
        try:
            return SubjectVisit.objects.get(
                appointment__visit_definition__code=self.visit_code,
                appointment__registered_subject=self.registered_subject)
        except SubjectVisit.DoesNotExist:
            return None

    @property
    def subject_requisition(self):
        model = self.receive.requisition_model_name
        RequisitionModel = models.get_model('bcpp_lab', model)
        try:
            return RequisitionModel.objects.get(
                requisition_identifier=self.receive.requisition_identifier)
        except RequisitionModel.DoesNotExist:
            return None

    @property
    def optional_description(self):
        """See PackingListHelper."""
        try:
            return self.subject_requisition.optional_description
        except AttributeError:
            return None

    def processing(self):
        url = reverse('admin:bcpp_lab_aliquotprocessing_add')
        return '<a href="{0}?aliquot={1}">process</a>'.format(url, self.pk)
    processing.allow_tags = True

    def related(self):
        url = reverse('admin:bcpp_lab_aliquot_changelist')
        return '<a href="{0}?q={1}">related</a>'.format(url, self.receive.receive_identifier)
    related.allow_tags = True

    class Meta:
        app_label = 'bcpp_lab'
        unique_together = (('receive', 'count'), )
        ordering = ('-created', 'count')
