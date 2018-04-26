#!/usr/bin/env python
"""This module computes similarities from the FFTs
of two sequences"""

import numpy as np
from scipy.stats import entropy as KL
from scipy.stats import pearsonr as PCC
# import preprocess_fft

##################################################

def kl_divergence(sequence_1, sequence_2):
    """Computes K-L divergence between two sequences"""

    np.seterr(invalid='ignore')
    abs_sequence_1 = np.nan_to_num(sequence_1)
    abs_sequence_2 = np.nan_to_num(sequence_2)
    # fft_sequence_1 = preprocess_fft.fft_abs(abs_sequence_1)
    # fft_sequence_2 = preprocess_fft.fft_abs(abs_sequence_2)
    min_length = min(len(abs_sequence_1), len(abs_sequence_2))
    kl_dvg = KL(abs_sequence_1[:min_length], abs_sequence_2[:min_length])
    return kl_dvg

##################################################

def pearson_coeff(sequence_1, sequence_2):
    """Computes Pearson's correlation coefficient between two sequences"""

    np.seterr(invalid='ignore')
    abs_sequence_1 = np.nan_to_num(sequence_1)
    abs_sequence_2 = np.nan_to_num(sequence_2)
    # fft_sequence_1 = preprocess_fft.fft_abs(abs_sequence_1)
    # fft_sequence_2 = preprocess_fft.fft_abs(abs_sequence_2)
    min_length = min(len(abs_sequence_1), len(abs_sequence_2))
    pcc, dummy_p_value = PCC(abs_sequence_1[:min_length], abs_sequence_2[:min_length])
    return pcc

##################################################

def main():
    """Main"""
    return

##################################################

if __name__ == "__main__":
    main()
