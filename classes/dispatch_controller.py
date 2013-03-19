import logging
from django.db.models import get_model
from django.core.exceptions import FieldError
from django.db.models import get_models, get_app, signals
from django.db.models.query import QuerySet
from bhp_visit_tracking.classes import VisitModelHelper
from bhp_lab_tracker.models import HistoryModel
from bhp_dispatch.classes import BaseDispatchController
from bhp_dispatch.exceptions import DispatchModelError
from bhp_base_model.models import BaseListModel
from lab_base_model.models import BaseLabListModel, BaseLabListUuidModel


logger = logging.getLogger(__name__)


class NullHandler(logging.Handler):
    def emit(self, record):
        pass
nullhandler = logger.addHandler(NullHandler())


class AlreadyDispatched(Exception):
    pass


class DispatchController(BaseDispatchController):

    def __init__(self, using_source,
                 using_destination,
                 user_container_app_label,
                 user_container_model_name,
                 user_container_identifier_attrname,
                 user_container_identifier,
                 dispatch_url,
                 **kwargs):
        super(DispatchController, self).__init__(using_source,
            using_destination,
            user_container_app_label,
            user_container_model_name,
            user_container_identifier_attrname,
            user_container_identifier,
            **kwargs)
        self._dispatch_url = None
        self._set_dispatch_url(dispatch_url)

    def _dispatch_prep(self):
        """Wrapper for user method :func:`dispatch_prep`."""
        self.dispatch_prep()

    def dispatch_prep(self):
        """Returns a list of RegisteredSubject instances.

        This is the main data query for dispatching and is to be overriden by the user
        to access local app models."""
        registered_subjects = []
        return registered_subjects

    def dispatch(self):
        """Dispatches items to a device by creating a dispatch item instance.

        ..note:: calls the user overridden :func:`dispatch_prep`."""
        # check source for the producer based on using_destination.
        if self.debug:
            logger.info("Dispatching items for {0}".format(self.get_user_container_identifier()))
        self._dispatch_prep()

    def _set_dispatch_url(self, value=None):
        """Sets the dispatch url for the dispatching model."""
        if not value:
            raise AttributeError('Dispatch url cannot be None. Set this in __init__() of the subclass.')
        self._dispatch_url = value

    def get_dispatch_url(self):
        """Gets the dispatch url for the dispatching model."""
        if not self._dispatch_url:
            self._set_dispatch_url()
        return self._dispatch_url

#    def set_visit_model_fkey(self, model_cls, visit_model_cls):
#        """Subject forms will have a foreign key to a visit model instance. This sets that foreign key."""
#        for fld in model_cls.objects._meta.fields:
#            if isinstance(fld, (ForeignKey, OneToOneField)):
#                if isinstance(fld.rel.to, visit_model_cls):
#                    self._visit_model_fkey_name = fld.name
#
#    def get_visit_model_fkey(self, app_label, model_cls, visit_model_cls=None):
#        """Gets the foreign key to the subject visit model instance."""
#        if not self._visit_model_fkey_name:
#            self.set_visit_model_fkey(model_cls, visit_model_cls)
#        return self._visit_model_fkey_name

    def dispatch_misc_instances(self, models, registered_subject, user_container, query_hint=None):
        """Sends any instance for dispatch as long as the class is configured for dispatch and has a relational path to registered subject.

            Args:
                models = a model class or list of model classes.
                registered_subject = instance of RegisteredSubject used to filter model class.
                user_container = the dispatch user container instance.
                query_hint = a django stype query string to registered subject.

            For example:
                    dispatch_misc_instances(
                        SubjectRcc,
                        registered_subject,
                        user_container,
                        query_hint='household_structure_member__registered_subject')
        """
        hint = []
        options = {}
        if not isinstance(models, list):
            models = [models]
        if query_hint:
            # convert the hint to an options dictionary for filter()
            options.update({query_hint: registered_subject})
            hint = query_hint.split('__')  # for error check
        else:
            hint.append('registered_subject')  # for error check
            options = {'registered_subject': registered_subject}

        for model_cls in models:
            # confirm that at least the first element of hint exists on the class
            if not hint[0] in dir(model_cls):
                raise DispatchModelError('Miscellaneous model classes sent for dispatch must have relational path to \'registered_subject\'. Your hint was \'{0}\' for model class {1}'.format('__'.join(hint), model_cls))
            # filter the class
            instances = model_cls.objects.filter(**options)
            if instances:
                self.dispatch_user_items_as_json(instances, user_container)

    def dispatch_list_models(self, app_name, base_cls=None):
        if not base_cls:
            base_cls = BaseListModel
        if not app_name:
            raise TypeError('Parameter app_name cannot be None.')
        app = get_app(app_name)
        for model_cls in get_models(app):
            if issubclass(model_cls, base_cls):
                self.model_to_json(model_cls)

    def dispatch_lab_list_models(self):
        self.dispatch_list_models('lab_clinic_api', (BaseLabListModel, BaseLabListUuidModel))

    def dispatch_lab_tracker_history(self, registered_subject, group_name=None):
        """Dispatches all lab tracker history models for this subject.

        ..seealso:: module :mod:`bhp_lab_tracker`.
        """
        if registered_subject:
            if registered_subject.subject_identifier:
                options = {'subject_identifier': registered_subject.subject_identifier}
                if group_name:
                    options.update({'group_name': group_name})
                history_models = HistoryModel.objects.filter(**options)
                if history_models:
                    self._to_json(history_models)

    def dispatch_appointments(self, registered_subject, user_container):
        """Dispatches all appointments for this registered subject.

        ..seealso:: module :mod:`bhp_appointment`
        """
        Appointments = get_model('bhp_appointment', 'Appointment')
        appointments = Appointments.objects.filter(registered_subject=registered_subject)
        if appointments:
            self.dispatch_user_items_as_json(appointments, user_container)

    def dispatch_scheduled_instances(self, app_label, registered_subject, user_container, **kwargs):
        """Sends scheduled instances to the producer for the given an instance of registered_subject.

        Keywords:
            kwargs must be field_attr: value pairs to pass directly to the visit model. Any django syntax will work.

        .. note::
           By scheduled_instances, we are referring to models that have a foreign key to a subclass
           of :mod:`bhp_visit_tracking`'s :class:`BaseVisitTracking` base model.
           For example, to maternal_visit, infant_visit, subject_visit, patient_visit, etc
        """
        
        # TODO: this and dispatch_requisitions() are duplications of the same function.
        
        #self.dispatch_appointments(registered_subject, user_container)
        # Get all the models with reference to SubjectVisit
        scheduled_models = self.get_scheduled_models(app_label)
        # get the visit model class for this app
        for scheduled_model_class in scheduled_models:
            visit_field_attname = VisitModelHelper.get_field_name(scheduled_model_class)
            scheduled_instances = scheduled_model_class.objects.filter(**{'{0}__appointment__registered_subject'.format(visit_field_attname): registered_subject})
            if scheduled_instances:
                self.dispatch_user_items_as_json(scheduled_instances, user_container)

    def dispatch_requisitions(self, app_label, registered_subject, user_container):
        """Dispatches all lab requisitions for this subject."""
        visit_field_attname = None
        requisition_models = self.get_requisition_models(app_label)
        for requisition_cls in requisition_models:
            if not visit_field_attname:
                visit_field_attname = VisitModelHelper.get_field_name(requisition_cls)
            requisitions = requisition_cls.objects.filter(**{'{0}__appointment__registered_subject'.format(visit_field_attname): registered_subject})
            if requisitions:
                self.dispatch_user_items_as_json(requisitions, user_container)

    def dispatch_entry_buckets(self, registered_subject):
        AdditionalLabEntryBucket = get_model('bhp_lab_entry', 'AdditionalLabEntryBucket')
        additional_lab_entry_bucket = AdditionalLabEntryBucket.objects.filter(registered_subject=registered_subject.pk)
        if additional_lab_entry_bucket:
            self._to_json(additional_lab_entry_bucket)
        ScheduledLabEntryBucket = get_model('bhp_lab_entry', 'ScheduledLabEntryBucket')
        scheduled_lab_entry_bucket = ScheduledLabEntryBucket.objects.filter(registered_subject=registered_subject.pk)
        if scheduled_lab_entry_bucket:
            self._to_json(scheduled_lab_entry_bucket)

    def dispatch_consent_instances(self, app_label, registered_subject, container, **kwargs):
        consent_models = self.get_consent_models(app_label)
        membershipform_models = self.get_membershipform_models()
        # remove classes that are also membership forms
        consent_models = [cls for cls in consent_models if cls not in membershipform_models]
        for consent_model in consent_models:
            consent_instances = consent_model.objects.filter(registered_subject=registered_subject)
            if consent_instances:
                self.dispatch_user_items_as_json(consent_instances, container)

    def dispatch_membership_forms(self, registered_subject, container, **kwargs):
        """Gets all instances of visible membership forms for this registered_subject and dispatches.

        Keywords:
            kwargs: must be field_attr: value pairs to pass directly to the visit model. Any django syntax will work.

        .. seealso::
            See app :mod:`bhp_visit` for an explanation of membership forms.
        """

        membershipform_models = self.get_membershipform_models()
        for membershipform_model in membershipform_models:
            try:
                if membershipform_model:
                    instances = membershipform_model.objects.filter(
                        registered_subject=registered_subject,
                        **kwargs)
            except FieldError:
                instances = membershipform_model.objects.filter(registered_subject=registered_subject)
            if instances:
                self.dispatch_user_items_as_json(instances, container)

    def dispatch_from_view(self, queryset, **kwargs):
        """Confirms no items in queryset are dispatched then follows by trying to dispatch each one.

        Does this by checking bhp_sync.outgoing_transactions in the netbook.
        """
        any_dispatched = False  # are any items dispatched already?
        any_transactions = True
        if not self.has_outgoing_transactions():
            any_transactions = False
            for qs in queryset:
                if qs.is_dispatched:
                    any_dispatched = True
                    break
            if not any_dispatched:
                for qs in queryset:
                    self.dispatch()
                self.dispatch_crypt()
                self.dispatch_registered_subjects()
        return any_dispatched, any_transactions

    def dispatch_crypt(self):
        logger.info("Updating the Crypt table...")
        self.update_model(('bhp_crypto', 'crypt'))

    def dispatch_registered_subjects(self):
        logger.info("Updating the Registered Subjects table...")
        self.update_model(('bhp_registration', 'RegisteredSubject'))