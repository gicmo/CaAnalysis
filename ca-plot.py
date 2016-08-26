#!/usr/bin/env python
# coding=utf-8

from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import argparse

import numpy as np
import pandas as pd
from scipy import stats

import matplotlib.pyplot as plt

from ca.util import get_nb_condition
from ca.nix import *
from ca.img import *

pulses = [1, 3, 10, 25]
ages = [10, 11, 13, 14, 15, 16, 17, 18, 60]


def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('--style', nargs='*', type=str, default=['ck'])
    parser.add_argument("file")
    parser.add_argument("pulse", choices=map(lambda p: 'ap'+str(p), pulses))
    args = parser.parse_args()

    plt.style.use(args.style)

    df = pd.read_csv(args.file if args.file != '-' else sys.stdin)

    over = df.Over.loc[1]
    dff = u'ΔG/R' if over == 'red' else u'ΔG/G'

    #control
    cdat = df.loc[df.Condition == 'control']
    cages = np.unique(cdat.Age)

    f, (ax1, ax2) = plt.subplots(1, 2, sharey=True)

    aged = cdat.groupby(['Age'])

    for age in cages:
        ax = ax1 if age < 20 else ax2
        ser = aged.get_group(age)
        d = np.array(ser[args.pulse])
        ax.scatter(np.tile(age, d.shape[0]), d, color='dodgerblue', alpha=0.5)
        sem = stats.sem(d, nan_policy='omit')
        mean = np.nanmean(d)
        ax.scatter(age, mean, color='black', s=30)
        ax.errorbar(age, mean, yerr=sem, color='black', capthick=1)

    ax1.spines['right'].set_visible(False)
    ax2.spines['left'].set_visible(False)
    ax2.yaxis.tick_right()

    d = .015
    kwargs = dict(transform=ax1.transAxes, color='k', clip_on=False)
    ax1.plot((1 - d, 1 + d), (-d, +d), **kwargs)
    ax1.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)

    kwargs.update(transform=ax2.transAxes)
    ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)
    ax2.plot((-d, +d), (-d, +d), **kwargs)

    ax1.set_xticks([10, 11, 12, 13, 14, 15, 16, 17, 18])
    ax2.set_xticks([55, 60, 65])

    ax2.set_xlabel('Postnatal day (P)')
    ax1.set_ylabel(dff)

    nbcond = get_nb_condition(df)

    # noisebox
    ndat = df.loc[df.Condition == nbcond]
    nages = np.unique(ndat.Age)
    aged = ndat.groupby(['Age'])

    plt.figure()
    for age in nages:
        ser = aged.get_group(age)
        d = np.array(ser[args.pulse])
        plt.scatter(np.tile(age, d.shape[0]), d, color='orange', alpha=0.5)
        sem = stats.sem(d, nan_policy='omit')
        mean = np.nanmean(d)
        plt.scatter(age, mean, color='black', s=30)
        plt.errorbar(age, mean, yerr=sem, color='black', capthick=1)

    plt.xlabel('Postnatal day (P)')
    plt.ylabel(dff)
    plt.xticks([a for a in nages])
    #both
    common = list(set(cages) & set(nages))

    gd = df.groupby(['Age', 'Condition'])

    plt.figure()
    offset = 0.0
    for age in common:
        nb = gd.get_group((age, nbcond))
        nb_sem = stats.sem(nb[args.pulse], nan_policy='omit')
        nb_mean = np.nanmean(nb[args.pulse])
        plt.scatter(age+offset, nb_mean, color='orange', s=30)
        plt.errorbar(age+offset, nb_mean, yerr=nb_sem, color='orange', capthick=1)

        cd = gd.get_group((age, 'control'))
        cd_sem = stats.sem(cd[args.pulse], nan_policy='omit')
        cd_mean = np.nanmean(cd[args.pulse])
        plt.scatter(age-offset, cd_mean, color='dodgerblue', s=30)
        plt.errorbar(age-offset, cd_mean, yerr=cd_sem, color='dodgerblue', capthick=1)

    plt.xlabel('Postnatal day (P)')
    plt.ylabel(dff)
    plt.xticks(common)
    plt.show()

if __name__ == "__main__":
    main()

