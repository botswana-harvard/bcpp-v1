from datetime import datetime

from django.db import models

from apps.bcpp_household.exceptions import AlreadyEnumerated, EligibleRepresentativeError

from ..constants import (BHS, BHS_ELIGIBLE, BHS_SCREEN, REFUSED, NOT_ELIGIBLE,
                         HTC_ELIGIBLE, REFUSED_HTC, HTC, ABSENT, UNDECIDED, BHS_LOSS)


class HouseholdMemberHelper(object):

    def __init__(self, household_member=None):
        self.household_member = household_member

    def member_status(self, selected_member_status):
        """Returns the member_status based on the boolean values set in the signals, mostly."""
        if self.household_member.is_consented:
            member_status = BHS
        elif self.household_member.eligible_subject and not self.household_member.refused:
            member_status = BHS_ELIGIBLE
        elif ((self.household_member.undecided or self.household_member.absent or
               self.household_member.refused)
              and selected_member_status == BHS_SCREEN):
            member_status = BHS_SCREEN
        elif ((self.household_member.absent or selected_member_status == ABSENT) and
              self.household_member.eligible_member):
            member_status = ABSENT
        elif ((self.household_member.absent or selected_member_status == ABSENT) and
              not self.household_member.eligible_member):
            member_status = NOT_ELIGIBLE
        elif self.household_member.undecided or selected_member_status == UNDECIDED:
            member_status = UNDECIDED
        elif ((self.household_member.refused or selected_member_status == REFUSED) and
              not self.household_member.eligible_htc and
              not self.household_member.htc and not self.household_member.refused_htc):
            member_status = REFUSED
        elif (self.household_member.refused and self.household_member.eligible_htc and
              not self.household_member.htc and not self.household_member.refused_htc):
            member_status = HTC_ELIGIBLE
        elif not self.household_member.eligible_member and not self.household_member.eligible_htc:
            member_status = NOT_ELIGIBLE
        elif (not self.household_member.eligible_subject and
              self.household_member.enrollment_checklist_completed and
              not self.household_member.eligible_htc):
            member_status = NOT_ELIGIBLE
        elif self.household_member.htc:
            member_status = HTC
        elif self.household_member.refused_htc:
            member_status = REFUSED_HTC
        elif not self.household_member.eligible_member and self.household_member.eligible_htc:
            member_status = HTC_ELIGIBLE  # e.g over 64yrs or just not eligible for BHS
        elif self.household_member.eligible_member and self.household_member.eligible_htc:
            member_status = HTC_ELIGIBLE  # e.g falied enrollment
        elif self.household_member.eligible_member:
            member_status = BHS_SCREEN  # new household_member instance
        else:
            pass
            # pprint.pprint(self.household_member.__dict__)
            # raise TypeError('cannot determine member_status. ')
        return member_status

    @property
    def member_status_choices(self):
        if not self.household_member.member_status:
            raise TypeError('household_member.member_status cannot be None')
        options = []
        if self.household_member.is_consented:
            # consent overrides everything
            options = [BHS]
        else:
            if not self.household_member.eligible_member:
                    if not self.household_member.eligible_htc:
                        options = [NOT_ELIGIBLE]
                    else:
                        if self.household_member.htc:
                            options = [HTC, BHS_SCREEN]
                        else:
                            options = [HTC_ELIGIBLE, BHS_SCREEN]
            elif self.household_member.eligible_member:
                options = [ABSENT, BHS_SCREEN, BHS_ELIGIBLE, BHS, UNDECIDED, REFUSED, BHS_LOSS, HTC, HTC_ELIGIBLE]
                if self.household_member.eligible_subject:
                        options.remove(BHS_LOSS)
                        options.remove(BHS_SCREEN)
                        options.remove(ABSENT)
                        options.remove(UNDECIDED)
                        if self.household_member.refused:
                            options.remove(BHS)
                            options.remove(BHS_ELIGIBLE)
                        if not self.household_member.refused:
                            options.remove(HTC)
                            options.remove(HTC_ELIGIBLE)
                if not self.household_member.eligible_subject:
                    options.remove(BHS_ELIGIBLE)
                    options.remove(BHS)
                    if self.household_member.refused:
                        options.remove(ABSENT)
                        options.remove(UNDECIDED)
                    if self.household_member.enrollment_loss_completed:
                        options.remove(BHS_LOSS)
                    if self.household_member.enrollment_checklist_completed:
                        options.remove(BHS_SCREEN)
                if not self.household_member.enrollment_checklist_completed:
                    options.remove(BHS_LOSS)
                if not self.household_member.eligible_htc:
                    options = [opt for opt in options if opt not in [HTC_ELIGIBLE, HTC]]
                elif self.household_member.eligible_htc:
                    options = [BHS_SCREEN]
            else:
                raise TypeError('ERROR: household_member.refused={0},self.household_member.eligible_htc={1}, '
                                'self.household_member.eligible_member={2} '
                                'should never occur together'.format(self.household_member.refused,
                                                                     self.household_member.eligible_htc,
                                                                     self.household_member.eligible_member))
        # append the current member_status
        options.append(self.household_member.member_status)
        # sort and remove duplicates
        options = list(set(options))
        options.sort()
        return [(item, item) for item in options]
