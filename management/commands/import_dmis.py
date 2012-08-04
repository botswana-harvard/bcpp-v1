from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from lab_import_dmis.classes import DmisLock, Dmis


class Command(BaseCommand):

    args = 'db --list-locks <lock_name> --unlock <lock_name> --import'
    help = 'Manage dmis import.'
    option_list = BaseCommand.option_list + (
        make_option('--list-locked',
            action='store_true',
            dest='list-locked',
            default=False,
            help=('List all locks.')),
         )
    option_list += (
        make_option('--unlock',
            action='store_true',
            dest='unlock',
            default=False,
            help=('Unlock for given lock name.')),
        )
    option_list += (
        make_option('--import',
            action='store_true',
            dest='import',
            default=False,
            help=('Import labs from dmis.')),
        )

    def handle(self, *args, **options):
        if not args:
            raise CommandError('Try --help for a list of valid options')
        args = list(args)
        db = args.pop(0)
        if not args:
            args = [None]
        dmis_lock = DmisLock(db)
        if options['list-locked']:
            for lock_name in args:
                self.list(dmis_lock, lock_name)
        elif options['unlock']:
            for lock_name in args:
                self.unlock(dmis_lock, lock_name)
        elif options['import']:
            self.import_from_dmis()
        else:
            raise CommandError('Unknown option, Try --help for a list of valid options')

    def import_from_dmis(self):
        dmis = Dmis('lab_api')
        dmis.import_from_dmis(protocol=settings.PROJECT_NUMBER)

    def unlock(self, dmis_lock, lock_name):
        if lock_name:
            dmis_lock.release(lock_name)
        else:
            print 'Unable to released lock {0}. Try --list for a list of valid locks.'.format(lock_name)

    def list(self, dmis_lock, lock_name):
        qs = dmis_lock.list(lock_name)
        if qs:
            print 'Existing Locks:'
            for q in qs:
                print '  {0} created {1}'.format(q.lock_name, q.created)
        else:
            print 'No locks exist.'
