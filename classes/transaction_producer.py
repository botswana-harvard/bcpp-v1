import socket
from django.conf import settings
from django.db.models import get_model


class TransactionProducer(object):

    def __init__(self, **kwargs):

        if kwargs.get('hostname'):
            self.value = kwargs.get('hostname')
        else:
            self.value = '%s-%s' % (socket.gethostname().lower(), settings.DATABASES['default']['NAME'].lower())
        if len(self.value) > 25:
            raise ValueError('Transaction Producer name cannot exceed 25 characters.(hostname + settings.DATABASES[\'default\'][\'NAME\'])')

    def __get__(self, instance, owner):
        return self.value

    def __str__(self):
        return self.value

    def has_outgoing_transactions(self, **kwargs):
        retval = False
        using = kwargs.get('using', 'default')
        producer_name = kwargs.get('producer_name', self.value)
        OutgoingTransaction = get_model('bhp_sync', 'outgoingtransaction')
        Producer = get_model('bhp_sync', 'producer')
        if not Producer.objects.using(using).filter(name=producer_name).exists():
            raise AttributeError('Producer {0} is unknown. Cannot check for outgoing transactions. (Note: using database key \'{1}\')'.format(producer_name, using))
        if OutgoingTransaction.objects.using(using).filter(producer=producer_name, is_consumed=False):
            retval = True
        return retval
