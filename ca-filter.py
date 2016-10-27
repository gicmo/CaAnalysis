#!/usr/bin/env python
# coding=utf-8

from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import argparse
import pandas as pd

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
    parser.add_argument('--litter', dest='litter', default=None)
    parser.add_argument('--dendrite', dest='dendrite', default=None)
    parser.add_argument('-f,--field', dest='field', nargs='*', type=str, default=None)

    args = parser.parse_args()

    df = pd.read_csv(args.file if args.file != '-' else sys.stdin)

    if args.litter:
        df = do_filter(df, "Litter", args.litter, args.inverse)

    if args.dendrite:
        df = do_filter(df, "Dendrite", args.dendrite, args.inverse)

    if args.field is not None:
        ff = [x.split('=') for x in args.field]
        for k, v in ff:
            df = do_filter(df, k, v, args.inverse)

    df.to_csv(sys.stdout, index=False)

if __name__ == '__main__':
    main()
