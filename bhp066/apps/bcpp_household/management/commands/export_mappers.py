import csv
from optparse import make_option
from datetime import datetime
import os

from django.db.models import get_model
from django.core.management.base import BaseCommand

from edc.map.classes import site_mappers

from edc.base.model.fields.helpers.revision import site_revision


class Command(BaseCommand):
    """ A command to export mapper data as a wiki table."""
    args = 'community'
    help = 'Export mapper data as a wiki table.'
    option_list = BaseCommand.option_list
    option_list += (
        make_option('--wiki',
            action='store_true',
            dest='wiki',
            default=False,
            help=('Format output for mediawiki.')),
        )

    def handle(self, *args, **options):
        if options['wiki']:
            self.format_for_wiki()
        else:
            self.format_for_console()

    def format_for_console(self):
        Survey = get_model('bcpp_survey', 'Survey')
        site_mappers.sort_by_code()
        for mapper in site_mappers:
            if mapper.map_code not in ['00', '01']:
                print '\n{}'.format(str(mapper()))
                print '--------------'
                for item, values in mapper().survey_dates.iteritems():
                    print '  {}'.format(item)
                    for name in values._fields:
                        print '    {}: {}'.format(name, str(getattr(values, name)))
        current_survey = Survey.objects.current_survey()
        print '\nCurrent survey: {} from {} to {}.'.format(
            current_survey, current_survey.datetime_start, current_survey.datetime_end)
        print 'Current Mapper: {}'.format(str(site_mappers.current_mapper()))
        print('\nBHP066 Edc {} ({})\n'.format(site_revision.tag, site_revision.branch))

    def format_for_wiki(self):
        """Formats output as wiki table."""
        site_mappers.sort_by_code()
        body = []
        header = []
        for mapper in site_mappers:
            if mapper.map_code not in ['00', '01']:
                for item, values in mapper().survey_dates.iteritems():
                    body.append('|{}||{}||{}'.format(
                        str(mapper()),
                        item,
                        '{}'.format('||'.join([str(getattr(values, f)) for f in values._fields]))))
                    if not header:
                        header = [f for f in values._fields]
        header = ['Community', 'Survey'] + header
        print('{| class="wikitable sortable"\n')
        print('!{}\n|-\n'.format('!!'.join(header)))
        print('\n|-\n'.join(body))
        print('\n|}\n')
        print('\nBHP066 Edc {} ({})\n'.format(site_revision.tag, site_revision.branch))
