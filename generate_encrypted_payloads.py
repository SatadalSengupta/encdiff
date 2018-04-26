""" Generate random encrypted packets """

import string
import random
from os.path import join as opj
from os.path import exists as ope
from os.path import dirname as opd
from os import makedirs as omd
from datetime import datetime
from struct import pack
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Cipher import ARC2
from Crypto.Cipher import ARC4
from Crypto.Cipher import Blowfish
from Crypto.Cipher import CAST
from Crypto.Cipher import DES
from Crypto.Cipher import DES3
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Cipher import XOR
from Crypto.Hash import SHA
from Crypto.Util import Counter
from Crypto.PublicKey import RSA
import utility_pickle
import numpy as np

BINOM_P = 1.0
BINOM_N = 1504
KEY = "quick brownFox jumpsOver lazyDog"
CIPHER_ALGOS = ["AES", "ARC2", "ARC4", "Blowfish",
                "CAST", "DES", "DES3", "PKCS1_OAEP",
                "PKCS1_v1_5", "XOR", "UnEncrypted"]

##################################################

def get_packet_size(param_n=BINOM_N, param_p=BINOM_P):
    """ Returns packet size """
    return np.random.binomial(param_n, param_p, 1)

##################################################

def payload_to_bytes(payload):
    """Convert payload to bytes"""
    payload_str = ""
    for component in payload:
        byte_string = "{0:b}".format(component).zfill(8)
        payload_str += byte_string
    return payload_str

###############################################

def encrypt_packet(packet_payload, cipher_algo):
    """ Generate an encrypted packet from plaintext packet """

    if cipher_algo == "AES":
        init_vec = Random.new().read(AES.block_size)
        cipher = AES.new(KEY, AES.MODE_CBC, init_vec)
        encrypted_payload = cipher.encrypt(packet_payload)

    elif cipher_algo == "ARC2":
        init_vec = Random.new().read(ARC2.block_size)
        cipher = ARC2.new(KEY, ARC2.MODE_CBC, init_vec)
        encrypted_payload = cipher.encrypt(packet_payload)

    elif cipher_algo == "ARC4":
        nonce = Random.new().read(16)
        tempkey = SHA.new(KEY + nonce).digest()
        cipher = ARC4.new(tempkey)
        encrypted_payload = cipher.encrypt(packet_payload)

    elif cipher_algo == "Blowfish":
        block_size = Blowfish.block_size
        init_vec = Random.new().read(block_size)
        cipher = Blowfish.new(KEY, Blowfish.MODE_CBC, init_vec)
        plen = block_size - divmod(len(packet_payload), block_size)[1]
        padding = [plen]*plen
        padding = pack('b'*plen, *padding)
        encrypted_payload = cipher.encrypt(packet_payload + padding)

    elif cipher_algo == "CAST":
        init_vec = Random.new().read(CAST.block_size)
        cipher = CAST.new(KEY[:16], CAST.MODE_CBC, init_vec)
        encrypted_payload = cipher.encrypt(packet_payload)

    elif cipher_algo == "DES":
        init_vec = Random.new().read(DES.block_size)
        cipher = DES.new(KEY[:8], DES.MODE_CBC, init_vec)
        encrypted_payload = cipher.encrypt(packet_payload)

    elif cipher_algo == "DES3":
        init_vec = Random.new().read(DES3.block_size)
        cipher = DES3.new(KEY[:24], DES3.MODE_CBC, init_vec)
        encrypted_payload = cipher.encrypt(packet_payload)

    elif cipher_algo == "PKCS1_OAEP":
        key = RSA.importKey(open('./resources/ssl_keys/pubkey.der').read())
        cipher = PKCS1_OAEP.new(key)
        encrypted_payload = cipher.encrypt(packet_payload[:86])

    elif cipher_algo == "PKCS1_v1_5":
        key = RSA.importKey(open('./resources/ssl_keys/pubkey.der').read())
        cipher = PKCS1_v1_5.new(key)
        encrypted_payload = cipher.encrypt(packet_payload[:86])

    elif cipher_algo == "XOR":
        cipher = XOR.new(KEY)
        encrypted_payload = cipher.encrypt(packet_payload)

    elif cipher_algo == "UnEncrypted":
        encrypted_payload = packet_payload # Unencrypted

    else:
        encrypted_payload = "###INVALID###"

    return encrypted_payload

##################################################

def generate_packets(output_path, count_packets, cipher_algo):
    """ Generate encrypted packets """

    payloads = []

    if not ope(opd(output_path)):
        omd(opd(output_path))

    for packet_index in range(count_packets):
        time = packet_index
        length = get_packet_size()
        packet_payload = "".join(random.choice(
            string.ascii_letters + string.digits)
                                 for _ in range(length))
        encrypted_packet_payload = encrypt_packet(packet_payload, cipher_algo)
        data = np.fromstring(encrypted_packet_payload, dtype='uint8')
        data_bytes = payload_to_bytes(data)
        payloads.append((length, time, data_bytes))
        # if packet_index % 100 == 0:
        #     print "Packets created: {} out of {}".format(
        #         packet_index, count_packets)

    utility_pickle.pickle_dump(payloads, output_path)
    print "Pickled for cipher algo: {}".format(cipher_algo)

    return

###################################################

def main():
    """ Main """

    time_start = datetime.now()
    print "Code execution started at: {}".format(time_start)
    base_path = opj("./resources/encrypted_payloads")
    count_packets = 1000000 # number of packets
    for cipher_algo in CIPHER_ALGOS:
        generate_packets(opj(base_path, cipher_algo+".pickle"), count_packets, cipher_algo)
    time_end = datetime.now()
    print "Code execution completed at: {}".format(time_end)

    print "Time consumed: {}".format(time_end - time_start)

    return

##################################################

if __name__ == "__main__":
    main()

##################################################
