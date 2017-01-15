#!/usr/bin/env python
# coding=utf-8

from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import argparse
import pandas as pd
import scipy.stats
import numpy as np

import sys


def do_filter(df, key, value, inverse):
    if inverse:
        df = df[df[key].astype(str) != value]
    else:
        df = df[df[key].astype(str) == value]
    return df


def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("file")
    parser.add_argument("--not", dest='inverse', action="store_true", default=False)
    parser.add_argument("--alpha", dest='alpha', default=0.05)
    parser.add_argument('-a', dest='x', nargs='+', type=str, default=None)
    parser.add_argument('-b', dest='y', nargs='+', type=str, default=None)
    parser.add_argument('-t,--target', dest='target', type=str, default=None)
    parser.add_argument('test', choices=['ttest', 'mannwhitneyu', 'auto'])

    args = parser.parse_args()

    df = pd.read_csv(args.file if args.file != '-' else sys.stdin)

    x, y = df.copy(), df.copy()

    ff = [i.split('=') for i in args.x]
    for k, v in ff:
        x = do_filter(x, k, v, False)

    ff = [i.split('=') for i in args.y]
    for k, v in ff:
        y = do_filter(y, k, v, False) 

    a = np.array(filter(lambda x: not np.isnan(x), x[args.target]))
    b = np.array(filter(lambda x: not np.isnan(x), y[args.target]))

    Wa, pa = scipy.stats.shapiro(a)
    Wb, pb = scipy.stats.shapiro(b)

    nna = pa < args.alpha
    nnb = pb < args.alpha

    print ("alpha: %f" % args.alpha)
    print ("a is: %s [p: %f]" % (['maybe normal', 'not normal'][nna], pa))
    print ("b is: %s [p: %f]" % (['maybe normal', 'not normal'][nnb], pb))
    
    if args.test == 'auto':
        if nna or nnb:
            stest = 'mannwhitneyu'
        else:
            stest = 'ttest'
    else:
        stest = args.test

    if stest == 'ttest':
        s, p = scipy.stats.ttest_ind(a, b, nan_policy='omit')
    elif stest == 'mannwhitneyu':
        s, p = scipy.stats.mannwhitneyu(a, b)
        


    print("T: %s [%s]" % (stest, args.test))
    print("N: a: %d; b: %d" % (len(a), len(b)))
    print("s: %f" % s, file=sys.stderr)
    print("p: %f" % p, file=sys.stderr)
    if p < args.alpha:
        print("significantly different!")


if __name__ == '__main__':
    main()
