from django.db import models
from django.core.urlresolvers import reverse
from audit_trail.audit import AuditTrail
from bcpp.choices import DXCANCER_CHOICE  
from base_scheduled_visit_model import BaseScheduledVisitModel


class Cancer (BaseScheduledVisitModel):
    
    """CS002 - Medical Diagnoses - Cancer"""

    date_cancer = models.DateField(
        verbose_name="92. Date of the diagnosis of cancer:",
        help_text="",
        )

    dx_cancer = models.CharField(
        verbose_name="93. [Interviewer:] What is the cancer diagnosis as recorded?",
        max_length=45,
        choices=DXCANCER_CHOICE,
        help_text="",
        )
    
    history = AuditTrail()

    def get_absolute_url(self):
        return reverse('admin:bcpp_subject_cancer_change', args=(self.id,))

    class Meta:
        app_label = 'bcpp_subject'
        verbose_name = "Cancer"
        verbose_name_plural = "Cancer"
