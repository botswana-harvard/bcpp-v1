__authors__ = [
    '"Erik van Widenfelt" <ew2789@gmail.com>',
]

import os
from datetime import datetime
from bhp_crypto.classes import Crypter


def setup_new_keys():

    """ Utility to generate all new keys for the project."""

    datestring = datetime.today().strftime('%Y%m%d%H%M%S%f')
    crypter = Crypter()
    filenames = []
    for algorithm, value in crypter.VALID_MODES.iteritems():
        if not isinstance(value, dict):
            filenames.append(value)
        else:
            for filename in crypter.VALID_MODES.get(algorithm).itervalues():
                if not isinstance(filename, dict):
                    filenames.append(filename)
                else:
                    for filename in filename.itervalues():
                        filenames.append(filename)
    # backup existing keys
    try:
        path = 'keys_backup_{0}'.format(datestring)
        os.mkdir(path)
        print path
    except:
        raise TypeError('failed to create backup folder')
    for filename in filenames:
        try:
            oldpath = os.path.join(os.path.realpath('.'), filename)
            newpath = os.path.join(os.path.join(
                                       os.path.realpath('.'), path), filename)
            print filename
            os.rename(oldpath, newpath)
        except:
            print ('Failed to copy {0} to backup '
                  'folder {1}'.format(filename, path))
    crypter = Crypter()
    crypter.create_new_rsa_key_pairs(suffix='')
    crypter.create_new_salt(suffix='')
    crypter.create_aes_key(suffix='')
