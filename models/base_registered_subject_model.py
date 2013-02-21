from django.db import models
from django.db.models import get_app, get_models
from bhp_appointment_helper.models import BaseAppointmentHelperModel
from registered_subject import RegisteredSubject


class BaseRegisteredSubjectModel (BaseAppointmentHelperModel):

    """ Base model for models that need a key to RegisteredSubject.

    Such models may be listed by name in the ScheduledGroup model and thus
    trigger the creation of appointments. Other instances may be Additional
    forms which are link to a subject but not a time point (for example,
    a Death model or OffStudy model (see also AdditionalEntryBucket)

    Use this along with BaseRegisteredSubjectModelAdmin()

    .. seealso:: This class inherits methods from bhp_appointment_helper that create appointments if the model
                 is configured as a ScheduledGroup model. See base class :mod:`bhp_appointment_helper.classes.BaseAppointmentHelperModel`.

    """
    registered_subject = models.OneToOneField(RegisteredSubject)

    def get_subject_identifier(self):
        """Returns the subject_identifier."""
        return self.registered_subject.subject_identifier

    def get_visit_model(self, instance):
        """Returns the visit model which is a subclass of :class:`BaseVisitTracking`."""
        from bhp_visit_tracking.models.base_visit_tracking import BaseVisitTracking
        for model in get_models(get_app(instance._meta.app_label)):
            if isinstance(model(), BaseVisitTracking):
                return model
        raise TypeError('Unable to determine the visit model from instance {0} for app {1}'.format(instance._meta.model_name, instance._meta.app_label))

    def get_registered_subject(self):
        return self.registered_subject

    class Meta:
        abstract = True
