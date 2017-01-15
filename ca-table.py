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

import StringIO

from ca.nix import *
from ca.img import *

pulses = [1, 3, 10, 25]
ages = [10, 11, 13, 14, 15, 16, 17, 18, 60]


def plot_peaks(args, nf):
    import matplotlib.pyplot as plt
    b = item_of_type(nf.blocks, "dff.peak")
    tags = items_of_type(b.multi_tags, "pulse.avg@age")
    tags = filter(lambda x: x.name.endswith(args.pulse), tags)

    plt.figure()

    for a in ages:
        mt =  filter(lambda x: x.name.startswith("P%d" % a), tags)
        if len(mt) != 1:
            continue
        mt = mt[0]
        pos = np.array(mt.positions)
        data = np.array([mt.retrieve_data(p, 0)[0] for p in range(len(pos))])
        plt.scatter(np.tile(a, len(data)), data, label='P%d'% a, color='blue')
        plt.scatter(a, np.mean(data), label='P%d-mean'% a, color='red')

    plt.ylim([-0.1, 1.4])
    plt.show()


def map_refs(tag):
    return {item_of_type(tag.references, "pulse.%d.max.avg" % i): i for i in pulses}


def neuron_name(nid):
    return "%d%c" % (int(nid) >> 8, chr(ord('a') + int(nid) & 0xFF))


def index_of_name(lst, name):
    for idx, entity in enumerate(lst):
        if entity.data.name == name:
            return idx
    return -1


def neuron_dendrite_length(full, neuron):
    n = None
    for n in full.data_arrays:
        if n.name.startswith(neuron):
            break
        n = None
    if n is None:
        return np.NaN
    return n.shape[0]


def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('--stdout', action="store_true", default=False)
    parser.add_argument("megatable")
    parser.add_argument("file")

    args = parser.parse_args()

    nf = nix.File.open(args.file, nix.FileMode.ReadOnly)

    full = item_of_type(nf.blocks, "dff.full")
    b = item_of_type(nf.blocks, "dff.peak")
    tag = item_of_type(b.multi_tags, "pulse.avg")

    pos = np.array(tag.positions)

    fneu = index_of_name(tag.features, "neuron")
    fcnd = index_of_name(tag.features, "condition")
    fage = index_of_name(tag.features, "age")

    params = nf.sections['params']
    baseline = params['baseline']
    over = params['over']
    dlen = params['length']
    pst = params['peak-start'] if 'peak-start' in params else None
    pnd = params['peak-end'] if 'peak-end' in params else None
    bg = params['bg-correction'] if 'bg-correction' in params else None

    # print("neuron feature @ %d " % fneu, file=sys.stderr)
    # print("condition feature @ %d " % fcnd, file=sys.stderr)
    # print("age feature @ %d " % fage, file=sys.stderr)

    peak_ind = "_".join(map(str, filter(lambda x: x is not None, [pst, pnd])))

    print("baseline: %s" % baseline, file=sys.stderr)
    print("over correction: %s" % over, file=sys.stderr)
    print("dendrite length: %s" % dlen, file=sys.stderr)
    print("background correction: %s" % (bg or 'uncorrected'), file=sys.stderr)
    print("peak range: %s" % peak_ind)
    outfile = StringIO.StringIO('')

    print('Neuron,Age,Condition,Over,Length,%s,%s,%s,%s'
          % tuple(map(lambda t: t.name.split('.')[0], tag.references)),
          file=outfile)

    for p in pos:
        p = int(p)
        nid = tag.retrieve_feature_data(p, fneu)[0]
        neuron = neuron_name(nid)
        cid = tag.retrieve_feature_data(p, fcnd)[0]
        condition = ['control', 'noisebox'][cid]
        age = tag.retrieve_feature_data(p, fage)[0]
        dlen = neuron_dendrite_length(full, neuron)
        print('%s,%d,%s,%s,%s,' % (neuron, age, condition, over, dlen), end='', file=outfile)
        data = [tag.retrieve_data(p, idx)[0] for idx, _ in enumerate(pulses)]
        print(",".join(map(str, data)), file=outfile)

    # Now we construct the giga table
    outfile.seek(0)

    imga = pd.read_csv(outfile)
    mega = pd.read_csv(args.megatable)

    result = pd.merge(mega, imga, how='inner', on=['Neuron'])
    result.reset_index(inplace=True)

    rename = {c: c[:-2] for c in result.columns if c.endswith("_x")}
    result.rename(columns=rename, inplace=True)

    filename = "img.%s.%s.%s.%s.%s.csv" % (over, baseline, dlen, peak_ind, (bg or 'uc'))
    result.to_csv(filename if not args.stdout else sys.stdout, index=False)
    if not args.stdout:
        print("\ndone, data written to:\n%s\n" % filename)

if __name__ == "__main__":
    main()

