#!/usr/bin/env python
# coding=utf-8

from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import argparse
import pandas as pd
import numpy as np

from ca.util import get_nb_condition
from ca.cmd import RangedAction

import matplotlib.pyplot as plt

pulses = [1, 3, 10, 25]

age_to_color = {10: [0xFF, 0xAA, 0x00],
                11: [0xCC, 0x00, 0x52],
                13: [0x00, 0xCC, 0x67],
                14: [0x00, 0x87, 0xCC],
                15: [0x00, 0x00, 0x99],
                16: [0x99, 0x99, 0x99],
                17: [0xCC, 0x88, 0x00],
                18: [0x99, 0x99, 0x7A],
                60: [0xFF, 0x55, 0x00]}


def col_age_to_color(col):
    for a in col['Age']:
        yield list(map(lambda x: x/0xFF, age_to_color[a]))


def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('--style', nargs='*', type=str, default=['ck'])
    parser.add_argument("imaging")
    parser.add_argument('column')
    parser.add_argument("--pulse", choices=map(lambda p: 'ap'+str(p), pulses), default='ap25')
    parser.add_argument("--age", action=RangedAction, type=str, default=None)
    parser.add_argument("--noisebox", default=False, action='store_true')
    args = parser.parse_args()

    plt.style.use(args.style)

    result = pd.read_csv(args.imaging)

    if args.age is not None:
        result = result.loc[result['Age'].isin(list(map(lambda a: int(a), args.age)))]

    nbcond = get_nb_condition(result)

    control = result.loc[result['Condition'] == "control"]
    noisebox = result.loc[result['Condition'] == nbcond]

    column = args.column
    plt.scatter(control[column], control[args.pulse], color=list(col_age_to_color(control)), alpha=0.5)

    if args.noisebox:
        plt.scatter(noisebox[column], noisebox[args.pulse], color=list(col_age_to_color(noisebox)),
                    alpha=0.5, facecolors='none', marker='D', lw=1.2)

    plt.ylabel('Calcium [%s]' % args.pulse)
    plt.xlabel('Ephys: [%s]' % column)

    plt.show()

if __name__ == "__main__":
    main()

