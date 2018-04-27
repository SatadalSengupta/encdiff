#!/usr/bin/env python
"""This module plots features"""

import itertools
from collections import Counter
from os.path import exists as ope
from os.path import dirname as opd
from os import makedirs as omd
from datetime import datetime
from math import log10
import numpy as np
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import seaborn as sns
import fetch_and_conserve as fnc
import generate_encrypted_payloads as gep

##################################################

CIPHER_ALGOS = ["AES", "ARC2", "ARC4", "Blowfish",
                "CAST", "DES", "DES3", "PKCS1_OAEP",
                "PKCS1_v1_5", "XOR", "UnEncrypted"]

##################################################

def get_label(feature_label):
    """ Returns corresponding verbose label for input feature label """

    if feature_label == "length":
        verbose_label = "Packet-size (PS)"
    elif feature_label == "mavg_length":
        verbose_label = "Packet-size Moving Average (PSMA)"
    elif feature_label == "mvar_length":
        verbose_label = "Packet-size Moving Variance (PSMV)"
    elif feature_label == "rel_time":
        verbose_label = r"Inter-arrival time (IAT) ($\mu$sec)"
    elif feature_label == "mavg_rel_time":
        verbose_label = r"Inter-Packet Timing Average (IPTA) ($\mu$sec)"
    elif feature_label == "mvar_rel_time":
        verbose_label = r"Inter-Packet Timing Variance (IPTV) (sq. $\mu$sec)"
    elif feature_label == "kldvg":
        verbose_label = "Kullback-Leibler Divergence (KLD)"
    elif feature_label == "mavg_kldvg":
        verbose_label = "Kullback-Leibler Divergence Average (KLDA)"
    elif feature_label == "mvar_kldvg":
        verbose_label = "Kullback-Leibler Divergence Variance (KLDV)"
    elif feature_label == "pcc":
        verbose_label = "Pearson's Correlation Coefficient (PCC)"
    elif feature_label == "mavg_pcc":
        verbose_label = "Pearson's Correlation Coefficient Average (PCCA)"
    elif feature_label == "mvar_pcc":
        verbose_label = "Pearson's Correlation Coefficient Variance (PCCV)"

    return verbose_label

##################################################

def plot_seaborn_ciphers(feature_label, plot_data):
    """ Plots using seaborn. Input format: {'label1':(xvals1, yvals1),
     'label2':(xvals2, yvals2), ...} """

    sns.set(style="ticks", font_scale=1.4)
    # font = {'weight' : 'bold', 'size' : 14}
    # matplotlib.rc('font', **font)

    cs_labels = CIPHER_ALGOS

    plt.xlabel(get_label(feature_label))
    plt.ylabel("CDF")
    plt.xscale("log")

    if feature_label in ["mvar_pcc", "mvar_kldvg"]:
        plt.xlim(10**-6, 10**-3)
    elif feature_label in ["mavg_kldvg"]:
        plt.xlim(2.7*10**-1, 3.2*10**-1)

    marker = itertools.cycle(("o", "v", "p", "d", "h", "s", "^"))
    linestyle = itertools.cycle(("-", "-.", "--", ":"))

    for i, cs_label in enumerate(cs_labels):
        (xvals, yvals) = plot_data[cs_label]
        plt.plot(xvals, yvals, label=cs_label,
                 linestyle=linestyle.next(), linewidth=1,
                 marker=marker.next(), markersize=5)

    fig_path = "./resources/plots/{}.pdf".format(feature_label)
    if not ope(opd(fig_path)):
        omd(opd(fig_path))

    plt.legend()
    plt.tight_layout()
    plt.savefig(fig_path, format="pdf")
    plt.clf()

    return

##################################################

def generate_cdf(data_points):
    """ Returns empirical CDF for provided set of data points """

    freq_dist = Counter(data_points)
    xvals = sorted(freq_dist.keys())

    pos_nz = 0

    for i, xval in enumerate(xvals):
        if xval > 0:
            pos_nz = i
            break
    xvals = xvals[pos_nz:]

    plot_xvals = np.logspace(start=log10(xvals[0]), stop=log10(xvals[-1]), num=100, base=10)
    plot_yvals = []

    cum_freq = 0
    last_pos = 0

    for plot_xval in plot_xvals:
        for xval in xvals[last_pos:]:
            if xval > plot_xval:
                break
            cum_freq += freq_dist[xval]
            last_pos += 1
        plot_yvals.append(cum_freq/float(len(data_points)))

    return plot_xvals, plot_yvals

##################################################

def plot_feature_values(reset=False):
    """ This method plots feature values """

    feature_labels = ["kldvg", "mavg_kldvg", "mvar_kldvg",
                      "pcc", "mavg_pcc", "mvar_pcc"]

    cipher_algos = CIPHER_ALGOS

    x_train, y_true = fnc.fnc_ground_truth(cipher_algos, feature_labels, reset)

    print "Starting feature-wise data-plotting"

    for seq_no, feature_label in enumerate(feature_labels):

        data_points = {}
        #
        for cipher_algo in cipher_algos:
            data_points[cipher_algo] = []
        #
        for (feature_vector, cipher_algo) in zip(x_train, y_true):
            data_points[cipher_algo].append(feature_vector[seq_no])
        #
        plot_datasets = {}
        for cipher_algo in cipher_algos:
            xvals, yvals = generate_cdf(data_points[cipher_algo])
            plot_datasets[cipher_algo] = (xvals, yvals)

        print "Plotting for feature: " + feature_label
        plot_seaborn_ciphers(feature_label, plot_datasets)

    print "Done!"

    return

##################################################

def main():
    """ Main """

    time_start = datetime.now()
    print "Code execution started at: {}".format(time_start)

    # gep.generate_encrypted_packets()
    plot_feature_values()

    time_end = datetime.now()
    print "Code execution completed at: {}".format(time_end)
    print "Time consumed: {}".format(time_end - time_start)

    return

##################################################

if __name__ == "__main__":
    main()

##################################################
