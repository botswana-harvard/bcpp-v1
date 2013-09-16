from base_subject_dashboard import BaseSubjectDashboard
from bcpp_subject.models import SubjectConsent, SubjectVisit, SubjectLocator
from bcpp_lab.models import SubjectRequisition, PackingList


class SubjectDashboard(BaseSubjectDashboard):

    view = 'subject_dashboard'
    dashboard_name = 'Subject Dashboard'

    def __init__(self, *args, **kwargs):
        kwargs.update({'dashboard_models': {'subject_consent': SubjectConsent}})
        super(SubjectDashboard, self).__init__(*args, **kwargs)

    def add_to_context(self):
        super(SubjectDashboard, self).add_to_context()
        self.context.add(
            home='bcpp',
            search_name='subject',
            subject_dashboard_url='subject_dashboard_url',
            title='Research Subject Dashboard',
            subject_consent=self.get_consent(),
            )

    def set_dashboard_type_list(self):
        self._dashboard_type_list = ['subject']

    def set_consent(self):
        """Sets to the subject consent, if it has been completed."""
        self._consent = None
        if SubjectConsent.objects.filter(subject_identifier=self.get_subject_identifier()):
            self._consent = SubjectConsent.objects.get(subject_identifier=self.get_subject_identifier())

    def get_visit_model(self):
        return SubjectVisit

    def get_requisition_model(self):
        return SubjectRequisition

    def get_locator_model(self):
        return SubjectLocator

    def get_locator_scheduled_visit_code(self):
        """ Returns visit where the locator is scheduled, TODO: maybe search visit definition for this?."""
        return '1000'

    def get_packing_list_model(self):
        return PackingList

    def render_labs(self, update=False):
        return ''
