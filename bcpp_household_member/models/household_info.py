from django.core.exceptions import ValidationError
from django.db import models

from edc_base.model.fields import OtherCharField
from edc_base.model.models import HistoricalRecords
from edc_base.model.validators import datetime_not_future

from bcpp.models import RegisteredSubject
from bcpp_household.models import HouseholdStructure
from bcpp_list.models import ElectricalAppliances, TransportMode
from bcpp_subject.choices import (
    FLOORING_TYPE, WATER_SOURCE, ENERGY_SOURCE, TOILET_FACILITY, SMALLER_MEALS)

from ..managers import HouseholdInfoManager

from .household_member import HouseholdMember
from .model_mixins import HouseholdMemberModelMixin


class HouseholdInfo(HouseholdMemberModelMixin):
    """A model completed by the user that captures household economic status
    from the Head of Household."""
    household_structure = models.OneToOneField(HouseholdStructure)

    household_member = models.OneToOneField(
        HouseholdMember,
        help_text=(
            'Important: The household member must verbally consent before completing this questionnaire.'),
    )

    registered_subject = models.OneToOneField(RegisteredSubject, editable=False)

    report_datetime = models.DateTimeField(
        verbose_name="Report Date/Time",
        validators=[datetime_not_future])

    flooring_type = models.CharField(
        verbose_name="What is the main type of flooring for this household?",
        max_length=25,
        choices=FLOORING_TYPE,
        help_text="")

    flooring_type_other = OtherCharField()

    living_rooms = models.IntegerField(
        verbose_name=(
            "How many living rooms are there in this household unit"
            " (exclude garage, bathroom, kitchen, store-room, etc if not used as living room )? "),
        null=True,
        blank=True,
        help_text=(
            "Note: Record the number of rooms where people live/meet/sleep. If participant does not"
            " want to answer, leave blank")
    )

    water_source = models.CharField(
        verbose_name="What is the main source of drinking water for this household? ",
        max_length=35,
        choices=WATER_SOURCE,
        help_text="")

    water_source_other = OtherCharField()

    energy_source = models.CharField(
        verbose_name="What is the main source of energy used for cooking? ",
        max_length=35,
        choices=ENERGY_SOURCE,
        help_text="")

    energy_source_other = OtherCharField()

    toilet_facility = models.CharField(
        verbose_name="What is the main toilet facility used in this household? ",
        max_length=35,
        choices=TOILET_FACILITY,
        help_text="")

    toilet_facility_other = OtherCharField()

    electrical_appliances = models.ManyToManyField(
        ElectricalAppliances,
        verbose_name=(
            "Does any member of this household have any of the following that are"
            " currently working? (check all that apply)."),
        blank=True,
        help_text=("Note: Please read each response to the participant and check all that apply. "
                   "If participant does not want to answer, leave blank."))

    transport_mode = models.ManyToManyField(
        TransportMode,
        verbose_name=(
            "Does any member of this household (excluding visitors) own any of the"
            " following forms of transport in working condition? (check all that apply)."),
        blank=True,
        help_text=("Note: Please read each response to the participant and check all that apply. "
                   "If participant does not want to answer, leave blank."))

    goats_owned = models.IntegerField(
        verbose_name=(
            "How many goats are owned by the members of this household?"
            " [If unsure of exact number, give your best guess] "),
        null=True,
        blank=True,
        help_text=("Note: May need to assist in adding up goats between household members"
                   " or helping estimate. If resident does not want to answer, leave blank."))

    sheep_owned = models.IntegerField(
        verbose_name=(
            "How many sheep are owned by the members of this household?"
            " [If unsure of exact number, give your best guess] "),
        null=True,
        blank=True,
        help_text=("Note: May need to assist in adding up sheep between household members"
                   " or helping estimate. If resident does not want to answer, leave blank."))

    cattle_owned = models.IntegerField(
        verbose_name=(
            "How many head of cattle (cows and bulls) are owned by the members"
            " of this household? [If unsure of exact number, give your best guess] "),
        null=True,
        blank=True,
        help_text=("Note: May need to assist in adding up cows and bulls between household members"
                   " or helping estimate. If resident does not want to answer, leave blank."))

    smaller_meals = models.CharField(
        verbose_name=(
            "In the past 4 weeks, did you or any household member have to eat a"
            " smaller meal than you felt you needed because there was not enough food? "),
        max_length=25,
        choices=SMALLER_MEALS,
        help_text="")

    objects = HouseholdInfoManager()

    history = HistoricalRecords()

    def natural_key(self):
        if not self.household_structure:
            raise AttributeError(
                "household_structure cannot be None for household_info with pk='\{0}\'".format(self.pk))
        return self.household_structure.natural_key()
    natural_key.dependencies = [
        'bcpp_household.household_structure',
        'bcpp_household.household_member',
        'registration.registered_subject']

    def save(self, *args, **kwargs):
        self.registered_subject = self.household_member.registered_subject
        self.verified_household_head(self.household_member)
        try:
            update_fields = kwargs.get('update_fields') + ['registered_subject', ]
            kwargs.update({'update_fields': update_fields})
        except TypeError:
            pass
        super(HouseholdInfo, self).save(*args, **kwargs)

    def verified_household_head(self, household_member, exception_cls=None):
        error_msg = None
        exception_cls = exception_cls or ValidationError
        if not household_member:
            raise exception_cls('No Household Member selected.')
        if not household_member.eligible_hoh:
            raise exception_cls('Household Member is not eligible Head Of Household. '
                                'Fill head of household eligibility first.')
        return error_msg

    class Meta:
        app_label = 'bcpp_household_member'
