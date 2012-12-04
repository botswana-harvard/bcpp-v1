import logging
from django.core.management.base import BaseCommand, CommandError
from bhp_dispatch.classes import DispatchController

logger = logging.getLogger(__name__)


class NullHandler(logging.Handler):
    def emit(self, record):
        pass
nullhandler = logger.addHandler(NullHandler())


class Command(BaseCommand):

    args = '<source> <destination>'
    help = 'Updates crypt model with recent instances from source to destination.'

    def handle(self, *args, **options):
        if not args or len(args) < 2:
            raise CommandError('Missing \'using\' parameters.')
        source = args[0]
        destination = args[1]
        dispatch_controller = DispatchController(source, destination)
        dispatch_controller.update_model(('bhp_crypto', 'crypt'))
