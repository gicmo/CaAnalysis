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


from ca.nix import item_of_type


def get_related_metadata(da, metadata, nf):
    md = da.metadata
    if md is None:
        md = nf.sections[da.name[:9]]
    return md[metadata]


def get_condition(da, nf):
    md = get_related_metadata(da, 'condition', nf)
    return md.lower()


def get_age(da, nf):
    md = get_related_metadata(da, 'age', nf)
    return md.lower()


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


def mk_sorter_by_age(nf):
    def _get_age(list_of_dataarrays):
        ld = list_of_dataarrays
        da = ld[0]
        return get_age(da, nf)
    return _get_age


def da_name_get_number(da):
    name = da.name
    return name.split('.')[2]


def read_exclude(path):
    lines = []
    with open(os.path.expanduser(path)) as pf:
        lines = pf.readlines()
    lines = list(map(lambda x: x.strip(), lines))
    return lines


def mk_filter_excludes(names):
    def _filter(g):
        name = g[0].name[:9]
        return name not in names
    return _filter


def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('--style', nargs='*', type=str, default=['ck'])
    parser.add_argument('--pulse', default='ap25')
    parser.add_argument('--age', default=None, type=int)
    parser.add_argument('--exclude', default='~/Data/exludes_tau.csv')
    parser.add_argument("file")

    args = parser.parse_args()

    excludes = read_exclude(args.exclude)
    print('%d excludes read!' % len(excludes), file=sys.stderr)

    nf = nix.File.open(args.file, nix.FileMode.ReadOnly)
    data = item_of_type(nf.blocks, "dff.mean")
    images = filter_pulses(data, args.pulse)
    images = sorted(images, key=lambda x: x.name[:9])
    grouped = reduce(group_by_name, images[1:], [[images[0]]])
    # print(len(set(map(lambda g: g[0].name[:9], grouped))), file=sys.stderr)
    grouped_filtered = list(filter(mk_filter_excludes(excludes), grouped))
    n_removed = len(grouped) - len(grouped_filtered)
    print('removed %d neuros' % (n_removed),
          file=sys.stderr)
    if n_removed != len(excludes):
        print("ERROR: number of excludes and removed neurons not the same!!")
        return -1
    grouped_sorted = sorted(grouped_filtered, key=mk_sorter_by_age(nf))
    lens = [imgs[0].shape[0] for imgs in grouped_sorted]
    alldata = np.empty((max(lens), sum([len(g) for g in grouped_sorted])))
    alldata[:] = np.NAN
    print("alldata matrix: %s" % str(alldata.shape), file=sys.stderr)
    count = 0
    names = []
    for g in grouped_sorted:
        first_da = g[0]
        neuron_name = first_da.name[:9]
        age = get_age(first_da, nf)
        condition = get_condition(first_da, nf)[0].upper()
        # print("- %s (%s, %s)" % (neuron_name, age, condition), file=sys.stderr)
        imgs = sorted(g, key=da_name_get_number)
        for i, img in enumerate(imgs):
            rep = i+1
            name = "%s_p%s_%s_%d" % (neuron_name, age, condition, rep)
            print("\t - [%s -> %s]" % (name, img.name), file=sys.stderr)
            alldata[:, count] = np.array(img[:])
            count += 1
            names.append(name)

    outfile = sys.stdout
    # output data
    print(",".join(names), file=outfile)
    for row in alldata:
        print(",".join(map(str, row)), file=outfile)


if __name__ == '__main__':
    main()
