#!/usr/bin/env python
# coding=utf-8

from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import argparse
import pandas as pd
import scipy.stats

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
    parser.add_argument('-f,--field', dest='field', nargs='*', type=str, default=None)
    parser.add_argument('-t,--target', dest='target', type=str, default=None)
     

    args = parser.parse_args()

    df = pd.read_csv(args.file if args.file != '-' else sys.stdin)

    if args.field is not None:
        ff = [x.split('=') for x in args.field]
        for k, v in ff:
            df = do_filter(df, k, v, args.inverse)

    df.to_csv(sys.stdout, index=False)

    W, p = scipy.stats.shapiro(df[args.target])
    print("N: %d" % len(df[args.target]))
    print("W: %f" % W, file=sys.stderr)
    print("p: %f" % p, file=sys.stderr)
    if p > args.alpha:
        print("Normally distributed (maybe)")
    else:
        print("NOT normally distributed (H0 rejected)")


if __name__ == '__main__':
    main()
