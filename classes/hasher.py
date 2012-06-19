import hashlib, base64
from django.core.exceptions import ValidationError
from django.conf import settings
from base_crypter import BaseCrypter


class Hasher(BaseCrypter):
    
    def __init__(self, *args, **kwargs):
        self.encrypted_salt = settings.SALT
        self.length = self._get_hash_length()
        self.iterations = 40
        super(Hasher, self).__init__( *args, **kwargs)
        if 'PRIVATE_KEY_LOCAL' in dir(settings):
            self.set_private_key(settings.PRIVATE_KEY_LOCAL)

    def new_hasher(self, value=''):
        return hashlib.sha256(value)
            
    def create_new_salt(self, value):
        return base64.b64encode(self.rsa_encrypt(value))
         
    def get_salt(self):
        if self.private_key:
            return self.rsa_decrypt(self.encrypted_salt)
        else:
            return None
    
    def _get_hash_length(self):
        return hashlib.sha256('Foo').block_size
        
    def get_hash(self, value, extra_salt=''):
        """ for a given value, return a salted SHA256 hash """
        if not value:
            retval = None
        else:
            # only change algorithm if existing hashes have been updated
            salt = self.get_salt()
            if salt:
                salt = salt+extra_salt
            if not isinstance(salt, str):
                raise ValidationError('The Encryption keys are not available to this system. Unable to save sensitive data.')
                #raise TypeError('Hasher expects \'salt\' to be a string.')
            digest = self.new_hasher(salt+value).digest()
            # then hash 40-1 times
            for x in range(0, self.iterations-1):
                digest = self.new_hasher(digest).digest()
            hash_value = digest.encode("hex")
            retval = hash_value
        return retval
    