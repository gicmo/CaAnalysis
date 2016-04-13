#!/usr/bin/env python
# coding=utf-8

from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os
import argparse

import datetime
import nixio as nix
import numpy as np

import matplotlib.pyplot as plt
import sys

from ca.nix import *
from ca.img import *

pulses = [1, 3, 10, 25]
ages = [10, 11, 13, 14, 15, 16, 17, 18, 60]


def plot_peaks(args, nf):
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


def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("file")

    args = parser.parse_args()

    nf = nix.File.open(args.file, nix.FileMode.ReadOnly)

    b = item_of_type(nf.blocks, "dff.peak")
    tag = item_of_type(b.multi_tags, "pulse.avg")

    pos = np.array(tag.positions)

    fneu = index_of_name(tag.features, "neuron")
    fcnd = index_of_name(tag.features, "condition")
    fage = index_of_name(tag.features, "age")

    params = nf.sections['params']
    over = params['over']
    dlen = params['length']

    # print("neuron feature @ %d " % fneu, file=sys.stderr)
    # print("condition feature @ %d " % fcnd, file=sys.stderr)
    # print("age feature @ %d " % fage, file=sys.stderr)

    print('Neuron,Age,Condition,Over,Length,%s,%s,%s,%s' % tuple(map(lambda t: t.name.split('.')[0], tag.references)))
    for p in pos:
        p = int(p)
        nid = tag.retrieve_feature_data(p, fneu)[0]
        neuron = neuron_name(nid)
        cid = tag.retrieve_feature_data(p, fcnd)[0]
        condition = ['control', 'noisebox'][cid]
        age = tag.retrieve_feature_data(p, fage)[0]
        print('%s,%d,%s,%s,%s,' % (neuron, age, condition, over, dlen), end='')
        data = [tag.retrieve_data(p, idx)[0] for idx, _ in enumerate(pulses)]
        print(",".join(map(str, data)))


if __name__ == "__main__":
    main()

