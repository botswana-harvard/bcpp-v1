from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from bhp_crypto.classes import BaseEncryptedField


class RestrictedRsaEncryptionField(BaseEncryptedField):
    
    """   private key is NOT expected to be available and it's absence is enforced """
    
    def __init__(self, *args, **kwargs):
        
        # check for settings attribute
        if not 'IS_SECURE_DEVICE' in dir(settings):
            raise ImproperlyConfigured('bhp_crypto requires boolean settings attribute IS_SECURE_DEVICE. Please add to your django settings file')
        # set alg, mode and defaults
        self.algorithm='rsa'
        self.mode='restricted-rsa'
        defaults={'help_text': kwargs.get('help_text', '')+' (Encryption: %s)' % (self.mode,) }
        kwargs.update(defaults)
        super(RestrictedRsaEncryptionField, self).__init__(*args, **kwargs)
        # setup the rsa keys
        self.crypter.set_public_key()
        self.crypter.set_private_key()
        # private key should not be on an insecure device
        if self.crypter.private_key:
            if not settings.IS_SECURE_DEVICE:
                print 'warning: {0} key {1} should not be installed on an insecure device.'.format(self.mode, self.get_private_keyfile())
