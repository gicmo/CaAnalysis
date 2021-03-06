#!/usr/bin/env python
# coding=utf-8

from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import argparse

import pandas as pd

import matplotlib.pyplot as plt

from ca.util import get_nb_condition
from ca.cmd import RangedAction
from ca.nix import *
from ca.img import *

pulses = [1, 3, 10, 25]


def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('--style', nargs='*', type=str, default=['ck'])
    parser.add_argument("imaging")
    parser.add_argument('x', type=str)
    parser.add_argument('y', type=str)
    parser.add_argument("--pulse", choices=map(lambda p: 'ap'+str(p), pulses), default='ap25')
    parser.add_argument("--age", action=RangedAction, type=str, default=None)
    parser.add_argument("--noisebox", default=False, action='store_true')
    args = parser.parse_args()

    plt.style.use(args.style)

    result = pd.read_csv(args.imaging)

    if args.age is not None:
        result = result.loc[result['Age'].isin(list(map(lambda a: int(a), args.age)))]

    nbcond = get_nb_condition(result)

    noisebox = result.loc[result['Condition'] == nbcond]
    result = result.loc[result['Condition'] == "control"]

    plt.scatter(result[args.x], result[args.y], c=result[args.pulse], cmap='plasma')

    if args.noisebox:
        plt.scatter(noisebox[args.x], noisebox[args.y], c=noisebox[args.pulse],
                    facecolors='none', marker='+', lw=1.2, cmap='plasma')

    plt.xlabel(args.x)
    plt.ylabel(args.y)
    plt.colorbar()

    plt.show()

if __name__ == "__main__":
    main()

