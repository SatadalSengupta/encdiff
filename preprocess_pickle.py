#!/usr/bin/env python
"""This module enables pickling of
packet payloads for FFT later"""

import sys
# from collections import Counter
import progressbar
import numpy as np
from scapy.all import rdpcap
import fetch_and_conserve as fnc

##################################################

def payload_to_bytes(payload):
    """Convert payload to bytes"""
    payload_str = ""
    for component in payload:
        byte_string = "{0:b}".format(component).zfill(8)
        payload_str += byte_string
    return payload_str

###############################################

def is_data_packet(pkt):
    """ Checks if packet is indeed a data packet """

    is_data_pkt = True
    if pkt.len <= 60:
        is_data_pkt = False

    return is_data_pkt

###############################################

def pickle_packets(trace_path, output_path):
    """Pickle packet payloads"""
    packets = rdpcap(trace_path)
    payloads = []

    bar = progressbar.ProgressBar(maxval=len(packets),
            widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()

    for i, pkt in enumerate(packets):
        try:
            time = int(float(pkt.time)*1000000) # Epoch time
            length = pkt.len # Packet length at IP layer
            data = np.fromstring(str(pkt.payload), dtype='uint8')
            if len(data) > 0 and is_data_packet(pkt):
                data_bytes = payload_to_bytes(data)
                payloads.append((length, time, data_bytes))
        except ValueError:
            pass
        finally:
            bar.update(i+1)
    
    bar.finish()

    fnc.pickle_dump(payloads, output_path)
    print "Pickled: " + trace_path

    return

###################################################

def main():
    """Main"""
    trace_path = sys.argv[1]
    output_path = sys.argv[2]
    pickle_packets(trace_path, output_path)

###################################################

if __name__ == "__main__":
    main()
    