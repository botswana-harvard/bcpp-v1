from edc_base.model.models import HistoricalRecords


from ..managers import HouseholdMemberManager

from .model_mixins import HouseholdMemberModelMixin


class SubjectUndecided (HouseholdMemberModelMixin):
    """A system model that links "undecided" information to a household member."""

    objects = HouseholdMemberManager()

    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        self.survey = self.household_member.survey
        self.registered_subject = self.household_member.registered_subject
        try:
            update_fields = kwargs.get('update_fields') + ['registered_subject', 'survey']
            kwargs.update({'update_fields': update_fields})
        except TypeError:
            pass
        super(SubjectUndecided, self).save(*args, **kwargs)

    def deserialize_prep(self, **kwargs):
        # SubjectUndecided being deleted by an IncommingTransaction, we go ahead and delete it.
        # This happens when we switch status from absentee and there are no absentee entries
        # attached to this SubjectUndecided.
        if kwargs.get('action', None) and kwargs.get('action', None) == 'D':
            self.delete()

    class Meta(HouseholdMemberModelMixin.Meta):
        app_label = 'bcpp_household_member'
        verbose_name = "Subject Undecided"
        verbose_name_plural = "Subject Undecided"
