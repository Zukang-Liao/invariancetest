# To save variance matrices at CONF level at args.plot_dir
# Input: load the .npy file (test_results1515.npy) generated by save_invariance_results.py
# Output: variance matrices
# Please specify --data_dir (where the .npy files are saved)
# The variance matrix plots will be generated in the same directory

import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
import collections
from utils import verify_paths, get_relations, merge_relations, get_asymmetry, get_continuity
from datamat import load_confidence_maps

import warnings
warnings.filterwarnings("ignore")

def argparser():
    parser = argparse.ArgumentParser()
    # The directory where the test_results1515.npy file is
    parser.add_argument("--data_dir", type=str, default="/datadir")
    # if you have specify other filename generated by save_invariance_results.py, please specify the generated filename here.
    parser.add_argument("--data_filename", type=str, default="")
    # if you have generated test_resultsxxxx.npy for other testing interval, rather than [-15, 15], please specify here.
    parser.add_argument("--plot_foldername", type=str, default="1515")

    # You must specify:
    parser.add_argument("--mid", type=str, default="-1") # model id
    # "r": rotation, "b": brightness, "s": scaling
    parser.add_argument("--aug_type", type=str, default="r")

    # Optonal:
    # If we split the data into correcly classified and misclassified examples
    parser.add_argument("--correct_split", type=bool, default=True)
    # If correct_split, whether we make the two splits the same number of data objects.
    parser.add_argument("--equal_split", type=bool, default=False)
    
    # Fixed parameters for this work:
    parser.add_argument("--seed", type=int, default=2)
    parser.add_argument("--flip_y", type=bool, default=True)
    parser.add_argument("--plot_detail", type=bool, default=False)
    parser.add_argument("--l2_norm", type=bool, default=True)
    parser.add_argument("--r", type=float, default=1.0) # ratio of data used
    parser.add_argument("--adv", type=bool, default=False)
    parser.add_argument("--epsilon", type=float, default=0.0)
    # Testing suite is either testing set or training set of the original dataset (CIFAR or MNIST)
    # In this work we only consider "testing set" as the testing suite.
    parser.add_argument("--train", type=bool, default=False)

    args = parser.parse_args()
    set_default_filename(args)
    args.data_path = os.path.join(args.data_dir, str(args.mid), args.data_filename)
    args.plot_dir = os.path.join(args.data_dir, str(args.mid), args.plot_foldername, "Confidence")
    return args


def set_default_filename(args):
    if args.data_filename == "":
        if args.aug_type == "r":
            args.data_filename = "test_results1515"
        else:
            args.data_filename = f"test_results0515{args.aug_type}"
        if args.adv:
            args.data_filename += f"_adv{args.epsilon}"
            args.plot_foldername += f"_adv{args.epsilon}"
        args.data_filename += ".npy"
    if "t" in args.mid:
        args.data_dir = args.data_dir+"_t"


def plot_variance_matrices_conf(args, class_id=None, test_intervals=None):
    # columns = ["idx", "label", "prediction", "confidence", "angle"]
    verify_paths(args)
    if args.train:
        _file_ext = " train.jpg"
    else:
        _file_ext = " test.jpg"

    def _plot_metric(arr, plot_title, plot_name, plot_sep=False):
        if args.flip_y:
            h, w = arr.shape
            plt.imshow(arr, extent=[0, w, 0, h])
        else:
            plt.imshow(arr)
        plt.axes().set_aspect("equal")
        plt.title(plot_title)
        plt.colorbar()
        if class_id is not None:
            plot_dir = os.path.join(args.plot_dir, f"Class{class_id}")
            plot_name = f"Class{class_id}_"+plot_name
        else:
            plot_dir = args.plot_dir
        if plot_sep and args.plot_detail:
            if args.train:
                plot_dir = os.path.join(plot_dir, "incorr_corr_sep_train")
            else:
                plot_dir = os.path.join(plot_dir, "incorr_corr_sep_test")
        if not os.path.exists(plot_dir):
            os.makedirs(plot_dir)
        plt.savefig(os.path.join(plot_dir, plot_name))
        plt.clf()
        
    if args.correct_split:
        incorr_confidence, corr_confidence, test_intervals = load_confidence_maps(args, class_id, test_intervals)
        if incorr_confidence.shape[1] == 0:
            incorr_confidence = corr_confidence
        nb_intv = len(test_intervals)
        nb_incorr = incorr_confidence.shape[1]
        nb_corr = corr_confidence.shape[1]
        corrcoefs, cos_dists, l2_dists = get_relations([incorr_confidence, corr_confidence], l2_norm=args.l2_norm, flip_y=args.flip_y)
        plot_title = f"\nIncorr (left):{nb_incorr}, corr (right):{nb_corr}"
        if class_id is not None:
            plot_title = f", class:{class_id}" + plot_title
        metric_names = ["corrcoef", "cos_dist", "l2_dist"]
        for m_idx, metrics in enumerate([corrcoefs, cos_dists, l2_dists]):
            mn = metric_names[m_idx]
            ctny, asymm = get_continuity(metrics, args.flip_y), get_asymmetry(metrics, args.flip_y)
            pt = plot_title + f"\nDiscontinuity: {ctny[0]:.3f}                  {ctny[1]:.3f}"
            pt += f"\nAsymmetry: {asymm[0]:.3f}                {asymm[1]:.3f}"
            merged = merge_relations([metrics], nb_intv)[0]
            _plot_metric(merged, f"mid: {args.mid}, {mn}"+pt, f"xconfidence {mn}"+_file_ext)
            if args.plot_detail:
                diff = np.subtract(metrics[0], metrics[1])
                _plot_metric(diff, f"diff_{mn}"+plot_title, f"dxconfidence {mn}"+_file_ext, plot_sep=True)
                _pt = f"All {nb_incorr} incorrect examples, {mn}\nDiscontinuity: {ctny[0]:.3f}, asymmetry: {asymm[0]:.3f}"
                _plot_metric(metrics[0], _pt, plot_name=f"incorr_xconf {mn}"+_file_ext, plot_sep=True)
                _pt = f"All {nb_corr} correct examples, {mn}\nDiscontinuity: {ctny[1]:.3f}, asymmetry: {asymm[1]:.3f}"
                _plot_metric(metrics[1], _pt, plot_name=f"corr_xconf {mn}"+_file_ext, plot_sep=True)
    else:
        data, test_intervals = load_confidence_maps(args, class_id, test_intervals)
        corrcoef, cos_dist, l2_dist = get_relations([data], l2_norm=args.l2_norm, flip_y=args.flip_y)
        # metric_names = ["corrcoef", "cos_dist", "l2_dist"]
        metric_names = ["l2_dist"]
        for m_idx, metrics in enumerate([l2_dist]):
            mn = metric_names[m_idx]
            _plot_metric(metrics[0], f"All {data.shape[1]} examples, {mn}", plot_name=f"all_example {mn}"+_file_ext, plot_sep=True)


if __name__ == "__main__":
    args = argparser()
    print(args)
    if args.aug_type == "r":
        test_intervals = [-15, 15]
        args.intv_centre = 0
    else:
        test_intervals=[0.7, 1.3]
        args.intv_centre = 1
    plot_variance_matrices_conf(args, class_id=None, test_intervals=test_intervals)
