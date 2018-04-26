"""This module does compute and saves result as pickle for future processing"""

from multiprocessing import Pool
from os.path import join as opj
from os.path import exists as ope
from os.path import basename as opb
from os.path import dirname as opd
from os import makedirs as omd
from os import listdir as old
from collections import Counter
from numpy import isnan, isinf
from utility_pickle import pickle_dump, pickle_load
from generate_encrypted_payloads import generate_packets
import preprocess_fft
import compute_fft_similarity
# import utility_sampling

##################################################

def get_rep_payloads(cipher_algo):
    """Generates representative payloads of specified size"""

    app_payload_path = "./resources/encrypted_payloads/{}.pickle".format(cipher_algo)

    dummy_flag, payloads = pickle_load(app_payload_path)

    representative_payloads = [(length, time, payload)
                               for (length, time, payload) in payloads]

    return representative_payloads

##################################################

def fnc_fft(cipher_algo, representative_payloads, reset=False):
    """Function generates and saves FFTs"""

    flag = False
    fft_objects = []
    fft_pickle_path = opj("resources", "cache", "fft",
                          "{}_fft.pickle".format(cipher_algo))
    if not ope(fft_pickle_path):
        flag = True
    else:
        print "Cache hit: {}".format(fft_pickle_path)
        dummy_flag, fft_objects = pickle_load(fft_pickle_path)
        if len(fft_objects) != len(representative_payloads):
            fft_objects = []
            flag = True

    if flag:
        # Parallelize FFT creation
        pool = Pool(processes=10)
        fft_objects = [pool.apply(preprocess_fft.fft_abs, args=(payload,))
                       for (dummy_length, dummy_time,
                            payload) in representative_payloads]

        pickle_dump(fft_objects, fft_pickle_path)

    return fft_objects

##################################################

def fnc_classification_data(cipher_algo, reset=False):
    """ Prepare data for classification """

    clf_path = opj("resources", "cache", "ground-truth-cipher-level",
                   "{}_clf.pickle".format(cipher_algo))
    classification_data = []

    if ope(clf_path) and (reset is False):
        print "Cache hit: {}".format(clf_path)
        dummy_flag, classification_data = pickle_load(clf_path)

    else:
        if not ope(opd(clf_path)):
            omd(opd(clf_path))
        payloads = get_rep_payloads(cipher_algo)
        fft_objects = fnc_fft(cipher_algo, payloads, reset)
        prev_time = payloads[0][1]
        #
        #
        mavg_length = 0
        mvar_length = 0
        #
        mavg_rel_time = 0
        mvar_rel_time = 0
        #
        mavg_kldvg = 0
        mvar_kldvg = 0
        #
        mavg_pcc = 0
        mvar_pcc = 0

        for number, (length, time, dummy_payload) in enumerate(payloads[1:]):

            mavg_length = (1.0*((mavg_length*number)+length))/(number+1)
            mvar_length = (1.0*(mvar_length*number)+((length-mavg_length)**2))/(number+1)

            rel_time = time - prev_time
            # Checks and bounds: Relative time can't be negative
            if rel_time < 0:
                rel_time = mavg_rel_time
            prev_time = time
            mavg_rel_time = (1.0*((mavg_rel_time*number)+rel_time))/(number+1)
            mvar_rel_time = (1.0*(mvar_rel_time*number)+((rel_time-mavg_rel_time)**2))/(number+1)
            # mstd_rel_time = mvar_rel_time**0.5

            kl_dvg = compute_fft_similarity.kl_divergence(
                fft_objects[number+1], fft_objects[number])
            # Checks and bounds: KL divergence value can't be inf or nan
            if isnan(kl_dvg) or isinf(kl_dvg):
                kl_dvg = mavg_kldvg
            mavg_kldvg = (1.0*((mavg_kldvg*number)+kl_dvg))/(number+1)
            mvar_kldvg = (1.0*(mvar_kldvg*number)+((kl_dvg-mavg_kldvg)**2))/(number+1)
            # mstd_kldvg = mvar_kldvg**0.5

            pcc = compute_fft_similarity.pearson_coeff(
                fft_objects[number+1], fft_objects[number])
            # Checks and bounds: Pearson's correlation coefficient value can't be inf or nan
            if isnan(pcc) or isinf(pcc):
                pcc = mavg_pcc
            mavg_pcc = (1.0*((mavg_pcc*number)+pcc))/(number+1)
            mvar_pcc = (1.0*(mvar_pcc*number)+((pcc-mavg_pcc)**2))/(number+1)
            # mstd_pcc = mvar_pcc**0.5

            data = {}
            #
            data["length"] = length
            data["mavg_length"] = mavg_length
            data["mvar_length"] = mvar_length
            #
            data["time"] = time
            data["rel_time"] = rel_time
            data["mavg_rel_time"] = mavg_rel_time
            data["mvar_rel_time"] = mvar_rel_time
            #
            data["kldvg"] = kl_dvg
            data["mavg_kldvg"] = mavg_kldvg
            data["mvar_kldvg"] = mvar_kldvg
            #
            data["pcc"] = pcc
            data["mavg_pcc"] = mavg_pcc
            data["mvar_pcc"] = mvar_pcc

            classification_data.append(data)

        pickle_dump(classification_data, clf_path)

    return classification_data

##################################################

def fnc_ground_truth(cipher_algos, feature_labels, reset=False):
    """ Prepares the ground truth (or training set) from input data """

    print "Ground truth data requested for: {}".format(", ".join(cipher_algos))
    ground_truth_path = opj("resources", "cache", "ground-truth-consolidated",
                            "ground_truth.pickle")

    if ope(ground_truth_path):
        print "Cache hit: {}".format(ground_truth_path)
        dummy_flag, (x_train, y_true) = pickle_load(ground_truth_path)

    else:
        print "Cache miss: {}".format(ground_truth_path)
        if not ope(opd(ground_truth_path)):
            omd(opd(ground_truth_path))
        #
        clf_datasets = []
        for cipher_algo in cipher_algos:
            clf_datasets.append(fnc_classification_data(cipher_algo, reset))
        print "Collected datasets for all cipher algos"
        #
        x_train = []
        y_true = []
        #
        for (cipher_algo, dataset) in zip(cipher_algos, clf_datasets):
            #
            for point in dataset:
                x_train.append([point[feature_label]
                                for feature_label in feature_labels])
                y_true.append(cipher_algo)
        #
        pickle_dump((x_train, y_true), ground_truth_path)
        print "Ground truth dataset counts: {}".format(", ".join(
            ["{}:{}".format(key, str(value))
             for key, value in Counter(y_true).iteritems()]))

    return x_train, y_true

##################################################

def main():
    """Main"""
    return

##################################################
