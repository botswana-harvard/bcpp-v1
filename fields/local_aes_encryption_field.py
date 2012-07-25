from bhp_crypto.classes import BaseEncryptedField


class LocalAesEncryptionField(BaseEncryptedField):

    """For encrypting long text """

    def __init__(self, *args, **kwargs):

        self.algorithm = 'aes'
        self.mode = 'local'
        defaults = {'help_text': kwargs.get('help_text', '') + ' (Encryption: {0})'.format(self.mode,)}
        kwargs.update(defaults)
        super(LocalAesEncryptionField, self).__init__(*args, **kwargs)
        self.crypter.set_aes_key()

    def have_decryption_key(self):
        retval = False
        if self.crypter.aes_key:
            retval = True
        return retval
