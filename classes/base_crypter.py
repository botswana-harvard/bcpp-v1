import os, base64
from datetime import datetime
from M2Crypto import Rand, RSA, EVP
from django.core.exceptions import ImproperlyConfigured
from base import Base


class BaseCrypter(Base):
    
    KEY_LENGTH=2048
    ENC=1
    DEC=0
    # prefix for each segment of an encrypted value, also used to calculate field length for model.
    prefix='enc1:::' # uses a prefix to flag as encrypted like django_extensions does
    secret_prefix='enc2:::'
    iv_prefix='iv:::'
    #default filenames for the pem files, salt and aes key
    #the "keys" in this dictionary may NOT be changed
    valid_modes={
        'rsa': {'irreversible-rsa': {'public': 'user-public-irreversible.pem'},
                'restricted-rsa': {'public': 'user-public-restricted.pem','private': 'user-private-restricted.pem'},
                'local-rsa':{'public': 'user-public-local.pem','private': 'user-private-local.pem'},
                },
        'aes': {'local-aes': 'user-aes-local.pem'},
        'salt': 'user-encrypted-salt.pem'
            }
 
    
    def __init__(self, *args, **kwargs):
        
        self.public_key=None
        self.private_key=None
        self.aes_key=None
        self.algorithm=None
        self.mode=None
        
    def set_public_key(self, keyfile=None, **kwargs):
        """ load public key using the pem filename. """
        if not self.public_key:
            algorithm=kwargs.get('algorithm', self.algorithm)
            mode=kwargs.get('mode', self.mode)
            if not keyfile:
                # keyfile not specified, so get the default for this algorithm and mode
                if not algorithm or not mode:
                    raise AttributeError('Algorithm and mode must be set before attempting to set the public key')
                keyfile=self.valid_modes.get(algorithm).get(mode).get('public')
            try:
                self.public_key=RSA.load_pub_key(keyfile)
            except:
                print 'warning: failed to load public key {0}.'.format(keyfile)

    def set_private_key(self, keyfile=None):
        """ load the private key using the pem filename """
        if not self.private_key:
            if not keyfile:
                # keyfile not specified, so get the default for this algorithm and mode
                if not self.algorithm or not self.mode:
                    raise AttributeError('Algorithm and mode must be set before attempting to set the private key')
                keyfile=self.valid_modes.get(self.algorithm).get(self.mode).get('private')               
            try:
                self.private_key = RSA.load_key(keyfile)
            except:
                pass
                #print 'Failed to load private key {0}.'.format(keyfile)
    
    def set_aes_key(self):
        """ Decrypt and set the AES key from a file using the local-rsa private key. """
        if not self.aes_key:
            try:
                f = open(self.get_aes_keyfile(), 'r')
                encrypted_key = f.read() 
                f.close()
                self.set_private_key(self.get_local_rsa_private_keyfile())
                if self.private_key:
                    self.aes_key = self.rsa_decrypt(encrypted_key)
            except:
                print 'warning: aes key {0} not found'.format(self.get_aes_keyfile())
            
    def get_local_rsa_private_keyfile(self):
        return self.valid_modes.get('rsa').get('local-rsa').get('private')
    
    def get_aes_keyfile(self):            
        return self.valid_modes.get('aes').get('local-aes')
       
    def _blank_callback(self): 
        "Replace the default dashes as output upon key generation" 
        return
    
    def create_new_rsa_key_pairs(self, suffix=str(datetime.today())):
        """ Create a new key-pair in the default folder, filename includes the current timestamp to avoid overwriting as existing key.
        * For now this can be called in the shell. 
        * Filename includes the current timestamp to avoid overwriting as existing key """        
        for mode_pair in self.valid_modes.get('rsa').itervalues():
            # Random seed 
            Rand.rand_seed (os.urandom (self.KEY_LENGTH)) 
            # Generate key pair 
            key = RSA.gen_key (self.KEY_LENGTH, 65537, self._blank_callback) 
            # create and save the public key to file
            filename=mode_pair.get('public', None)
            # key.save_pub_key('user-private-local.pem'), for example if suffix=''            
            key.save_pub_key(''.join(filename)+suffix) 
            # create and save the private key to file
            filename=mode_pair.get('private', None)
            # key.save_key('user-private-local.pem'), for example if suffix=''
            if filename:
                key.save_key(''.join(filename)+suffix, None) 
    
    def create_aes_key(self, public_keyfile=valid_modes.get('rsa').get('local-rsa').get('public'), suffix=str(datetime.today()), key=None):
        """ create and rsa encrypt a new AES key. Use the "local" public key.
        * Filename suffix is added to the filename to avoid overwriting an existing key """        
        if not key:
            key=os.urandom(16)
        if not public_keyfile:
            raise TypeError('Please specify the local public key filename. Got None')
        self.set_public_key(public_keyfile)
        filename=self.valid_modes.get('aes').get('local-aes')+suffix
        encrypted_aes_key=self.public_key.public_encrypt(key, RSA.pkcs1_oaep_padding)   
        f=open(filename, 'w') 
        f.write(base64.b64encode(encrypted_aes_key))
        f.close()
        #return base64.b64encode(encrypted_aes_key)
    
    def rsa_encrypt(self, plaintext, **kwargs):
        """Return an uncode encrypted value, but know that it may fail if keys are not available"""
        if not self.public_key:
            self.set_public_key(**kwargs)
        if not self.public_key:
            raise ImproperlyConfigured("RSA public key not set, unable to decrypt cipher.")
        if self.is_encrypted(plaintext):
            raise ValueError('Attempt to rsa encrypt an already encrypted value.')
        return self.public_key.public_encrypt(plaintext, RSA.pkcs1_oaep_padding)
    
    def rsa_decrypt(self, secret, is_encoded=True):
        """ Return cleaned decrypted cipher text if the private key is available. 
        Check for the private_key before calling this method.
        Cipher_text is base64 encoded unless is_encoded is false"""
        if not self.private_key:
            self.set_private_key()
        if not self.private_key:
            raise ImproperlyConfigured("RSA private key not set, unable to decrypt cipher.")
        if is_encoded:
            cipher_text = base64.b64decode(secret)
        return self.private_key.private_decrypt(cipher_text,
                                                RSA.pkcs1_oaep_padding).replace('\x00', '')
    
    def _build_cipher(self, key, iv, op=ENC):
        """"""""
        return EVP.Cipher(alg='aes_128_cbc', key=key, iv=iv, op=op)
                                                    
    def aes_decrypt(self, secret, is_encoded=True):
        """ Takes a tuple (secret_text, sep, iv)  """
        retval=secret
        if isinstance(secret, (list, tuple)):
            #cipher_tuple is (cipher, sep, iv)
            secret_text,iv=secret[0], secret[2]
        else:
            print 'warning: aes cipher_value should be a list or tuple'
            secret_text,iv=base64.b64decode(secret),'\0'*16
        if not self.aes_key:
            self.set_aes_key()
            #raise ImproperlyConfigured("AES key not set, unable to decrypt cipher.")       
        if self.aes_key:
            if is_encoded:
                secret_text=base64.b64decode(secret_text)
                iv=base64.b64decode(iv)
            cipher=self._build_cipher(self.aes_key, iv, self.DEC)
            v=cipher.update(secret_text)
            #print ('dec', self.aes_key,'', base64.b64encode(cipher_text))
            #try:
            v = v + cipher.final()
            #except:
            #    raise ValueError('AES decryption error. {0}, {1}, {2} cipher={3}'.format(self.algorithm, self.mode, self.aes_key, base64.b64encode(cipher_text)))
            del cipher
            retval = v.replace('\x00', '')
        return retval
    
    def aes_encrypt(self, plaintext):            
        """ Encrypt with AES, but fail if aes_key unavailable.
        Important to not allow any data to be saved if the keys are not available"""
        if not self.aes_key:
            self.set_aes_key()
            if not self.aes_key:
                # must FAIL here if key not available and user is trying to save unencrypted data
                raise ImproperlyConfigured('AES key not available, unable to encrypt sensitive data using the AES algorithm.')
        if self.is_encrypted(plaintext):
            raise ValueError('Attempt to aes encrypt an already encrypted value.')
        iv=os.urandom(16)
        cipher = self._build_cipher(self.aes_key, iv, self.ENC)
        v = cipher.update(plaintext)
        v = v + cipher.final()
        del cipher
        #print ('enc', self.aes_key, value, base64.b64encode(v))
        return (v,iv)

    def is_encrypted(self, value):
        """ The value string is considered encrypted if it starts with 'self.prefix' """
        if not value:
            retval = False
        else:
            if value == self.prefix:
                raise TypeError('Expected a string value, got just the encryption prefix.')
            if value.startswith(self.prefix):
                retval = True
            else:
                retval = False
        return retval
    
    def mask_encrypted(self, value, mask='<encrypted>'):
        """ help format values for display by masking them if encrypted at the time of display"""
        if self.is_encrypted(value):
            return mask
        else:
            return value
    
