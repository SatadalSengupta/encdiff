import cPickle as pickle
from os.path import join as opj
from os.path import exists as ope
from os.path import basename as opb
from os.path import dirname as opd
from os import makedirs as omd
from os import listdir as old

##################################################

def pickle_dump(obj, path):
    """ Wrapper around picle dump for handling
     cases where path doesn't exist """

    dirname = opd(path)
    if not ope(dirname):
        omd(dirname)

    fileptr = open(path, "wb")
    pickle.dump(obj, fileptr)
    fileptr.close()

    return

##################################################

def pickle_load(path):
    """ Wrapper around pickle load for open/close of pickle file
    and for cases where path doesn't exist """

    if not ope(path):
        flag = False
        obj = None
    else:
        try:
            flag = True
            fileptr = open(path, "rb")
            obj = pickle.load(fileptr)
            fileptr.close()
        except:
            print path
            raise

    return flag, obj

##################################################
