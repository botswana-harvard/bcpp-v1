import os
import csv

from django.core.management.base import BaseCommand, CommandError
from django.db.models import get_model

from apps.bcpp_household.constants import BASELINE_SURVEY_SLUG
from apps.bcpp_household_member.models import HouseholdMember


class Command(BaseCommand):

    args = 'community,community,... or all'
    help = 'Export columns subject_identifier, community to a csv file in your home folder'

    def handle(self, *args, **options):
        SubjectConsent = get_model('bcpp_subject', 'SubjectConsent')
        try:
            communities = args[0].split(',')
        except IndexError:
            raise CommandError('Expected at least one parameter for community')
        print 'Preparing list of subject_identifiers for communities {}'.format(', '.join(communities))
        n = 0
        filename = os.path.expanduser('~/subject_identifier_{}.csv')
        if args[0] == 'all':
            filename = filename.format('all')
        else:
            filename = filename.format('_'.join(communities))
        with open(filename, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['subject_identifier', 'community', 'subject_identifier_aka', 'dm_reference'])
            for hm in HouseholdMember.objects.filter(
                    household_structure__survey__survey_slug=BASELINE_SURVEY_SLUG,
                    registered_subject__subject_identifier__startswith='066',
                    household_structure__household__plot__community__in=communities,
                    ).order_by('registered_subject__subject_identifier'):
                n += 1
                try:
                    # hm.registered_subject attributes should equal subject_consent
                    SubjectConsent.objects.get(
                        household_member=hm,
                        subject_identifier=hm.registered_subject.subject_identifier,
                        subject_identifier_aka=hm.registered_subject.subject_identifier_aka,
                        )
                except SubjectConsent.DoesNotExist:
                    raise CommandError('Inconsistent identifiers between SubjectConsent and '
                                       'RegisteredSubject. Got {}.'.format(hm.registered_subject))
                writer.writerow(
                    [hm.registered_subject.subject_identifier,
                     hm.household_structure.household.plot.community,
                     hm.registered_subject.subject_identifier_aka,
                     hm.registered_subject.dm_comment]
                    )
        print 'Exported {} identifiers to {}'.format(n, filename)
