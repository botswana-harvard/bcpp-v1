import os
from datetime import datetime
from bhp_crypto.classes import Crypter
from bhp_crypto.classes.hasher import Hasher


def setup_new_keys():

    datestring = datetime.today().strftime('%Y%m%d%H%M%S%f')
    crypter=Crypter()
    filenames=[]
    for algorithm in crypter.valid_modes.iterkeys():
        for filename in crypter.valid_modes.get(algorithm).itervalues():
            if isinstance(filename, dict): 
                for filename in filename.itervalues():
                    filenames.append(filename)
            else:
                filenames.append(filename)
    # backup existing keys
    try:
        path='keys_backup_{0}'.format(datestring)
        os.mkdir(path)
        print path
    except:
        raise TypeError('failed to create backup folder')    
    

    for filename in filenames:
        try:
            oldpath=os.path.join(os.path.realpath('.'),filename)
            newpath=os.path.join(os.path.join(os.path.realpath('.'),path), filename)
            print filename
            os.rename(oldpath, newpath)
        except:
            print 'Failed to copy {0} to backup folder {1}'.format(filename, path)
    #create restricted RSA
    crypter=Crypter()
    crypter.create_new_rsa_key_pairs(suffix='')
    hasher=Hasher()
    hasher.set_public_key(crypter.valid_modes.get('rsa').get('local-rsa').get('public'))
    hasher.create_new_salt(suffix='')
    #create and encrypt AES key
    crypter.create_aes_key(suffix='')

   
