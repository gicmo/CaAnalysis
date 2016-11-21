#!/usr/bin/env python
# coding=utf-8

from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os
import argparse

import nixio as nix
import numpy as np
import pandas as pd

import sys

import matplotlib.pyplot as plt

from ca.nix import item_of_type

age_to_color = {10: [0xFF, 0xAA, 0x00],
                11: [0xCC, 0x00, 0x52],
                13: [0x00, 0xCC, 0x67],
                14: [0x00, 0x87, 0xCC],
                15: [0x00, 0x00, 0x99],
                16: [0x99, 0x99, 0x99],
                17: [0xCC, 0x88, 0x00],
                18: [0x99, 0x99, 0x7A],
                60: [0xFF, 0x55, 0x00]}


def filter_pulses(block, pulse):
    return [da for da in block.data_arrays if pulse in da.name]


def group_by_name(result, x):
    a_name = result[-1][-1].name[:9]
    b_name = x.name[:9]
    if a_name == b_name:
        result[-1].append(x)
    else:
        result.append([x])
    return result


def get_age(da, nf):
    md = da.metadata
    if md is None:
        md = nf.sections[da.name[:9]]
    age = int(md['age'])
    return age


def mk_sorter_by_age(nf):
    def _get_age(list_of_dataarrays):
        ld = list_of_dataarrays
        da = ld[0]
        return get_age(da, nf)
    return _get_age


def mk_filter_by_age(nf, target):
    def _age_filter(list_of_dataarrays):
        age = get_age(list_of_dataarrays[0], nf)
        return age == target
    return _age_filter


def get_condition(da, nf):
    md = da.metadata
    if md is None:
        md = nf.sections[da.name[:9]]
    return md['condition'].lower()


def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('--style', nargs='*', type=str, default=['ck'])
    parser.add_argument('--pulse', default='ap25')
    parser.add_argument('--start', default=12, type=int)
    parser.add_argument('--end', default=24, type=int)
    parser.add_argument('--age', default=None, type=int)
    parser.add_argument('--condition', default=None)
    parser.add_argument('--data', default=False, action='store_true')
    parser.add_argument('--igor', default=False, action='store_true')
    parser.add_argument("file")

    args = parser.parse_args()

    nf = nix.File.open(args.file, nix.FileMode.ReadOnly)
    full = item_of_type(nf.blocks, "dff.full")
    images = filter_pulses(full, args.pulse)
    if args.condition is not None:
        cnd = args.condition
        images = [img for img in images if cnd == get_condition(img, nf)]
    images = sorted(images, key=lambda x: x.name[:9])
    grouped = reduce(group_by_name, images[1:], [[images[0]]])
    start, end = args.start, args.end
    plt.figure()
    grouped_sorted = sorted(grouped, key=mk_sorter_by_age(nf))
    if args.age is not None:
        grouped_sorted = filter(mk_filter_by_age(nf, args.age), grouped_sorted)
    lens = [imgs[0].shape[0] for imgs in grouped_sorted]
    alldata = np.empty((max(lens), len(grouped_sorted)))
    alldata[:] = np.NAN
    print(alldata.shape, len(grouped_sorted), file=sys.stderr)
    if args.data:
        print("number,neuron,length,%s" % (
            ",".join(list(map(str, range(alldata.shape[0]))))
        ))
    for i, da in enumerate(grouped_sorted):
        name = da[0].name[:9]
        print("%d: %s [%d]" % (i, name, len(da[0])), file=sys.stderr)
        data = np.array([img[:, start:end].mean(axis=1) for img in da])
        mms = data.mean(axis=0).squeeze()
        alldata[:len(mms), i] = mms
        color = list(map(lambda x: x/0xFF, age_to_color[get_age(da[0], nf)]))
        if args.age is not None:
            plt.plot(mms, label='%0.2d - %s' % (i, name))
        else:
            plt.plot(mms, color=color)
        if args.data:
            print("%d,%s,%d,%s" % (
                i, name, len(mms),
                ",".join(list(map(lambda x: str(alldata[x, i]), range(alldata.shape[0]))))
            ))

    if args.igor:
        names = ["%s_p%d_%s" % (da[0].name[:9], get_age(da[0], nf), get_condition(da[0], nf)) for da in grouped_sorted]

        print(",".join(names))
        for k in range(alldata.shape[0]):
            for n in range(alldata.shape[1]):
                if n > 0:
                    print(",", end="")
                print("%f" % alldata[k, n], end="")
            print("")


    if args.age is not None:
        plt.legend(fontsize='7')

    plt.figure()
    plt.imshow(alldata.T, interpolation="none")
    plt.colorbar()
    plt.show()


if __name__ == '__main__':
    main()
