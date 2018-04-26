#!/usr/bin/env python
"""This module generates FFT from a given sequence"""

from numpy.fft import fft
import numpy as np

##################################################

def fft_abs(bit_sequence):
    """Generates absolute values of FFT from sequence"""
    sequence = [int(bit) for bit in bit_sequence]
    fft_sequence = np.nan_to_num(fft(sequence))
    fft_abs_sequence = np.absolute(fft_sequence)
    return fft_abs_sequence

##################################################

def main():
    """Main"""
    return

##################################################

if __name__ == "__main__":
    main()
    