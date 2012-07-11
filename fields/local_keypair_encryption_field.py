from bhp_crypto.classes import BaseEncryptedField
from django.core.exceptions import ImproperlyConfigured
from bhp_crypto.settings import settings


class LocalKeyPairEncryptionField(BaseEncryptedField):
    
    """  'local key-pair': same as 'restricted key-pair' but the private key is expected to be available and it's absence is not enforced """
    def __init__(self, *args, **kwargs):
        if not self.algorithm:
            raise TypeError('Instance attribute algorithm may not be None. Set to RSA or AES in the subclass')
        if not self.mode:
            raise TypeError('Mode may not be None. Set in the subclass')
        
        if self.mode not in self.crypter.files.iterkeys():
            raise KeyError('Invalid mode \'{mode}\' for algorithm {algorithm}. Must be one of {keys}'.format(mode=self.mode, algorithm=self.algorithm, keys=','.join(self.crypter.files.iterkeys)))
        super(LocalKeyPairEncryptionField, self).__init__(*args, **kwargs)
    
    def get_public_keyfile(self):
        if not hasattr(settings, 'PUBLIC_KEY_LOCAL'):
            raise ImproperlyConfigured('For \'%s\' security, you must set the PUBLIC_KEY_LOCAL setting to ' \
                                        'point to your public key (path and filename) .' % (self.mode,))
        return settings.PUBLIC_KEY_LOCAL 

    def get_private_keyfile(self):
        retval = None
        if 'PRIVATE_KEY_LOCAL' in dir(settings):
            # medium security expects a private key to be available on the device, 
            # but you could remove move it to fully de-identify the DB
            if settings.PRIVATE_KEY_LOCAL:
                retval = settings.PRIVATE_KEY_LOCAL
        return retval 
     
