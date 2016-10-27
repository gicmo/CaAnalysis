#!/usr/bin/env python
# coding=utf-8

from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import argparse
import sys
import os

import datetime
import nixio as nix
import numpy as np
import pandas as pd

from ca.nix import *
from ca.img import *

loops = {
    "1": [3,  1, 10, 1],
    "2": [3,  1, 25, 3],
    "3": [1, 25,  3, 1, 10]
}

pulses = [1, 3, 10, 25]

ages = [10, 11, 13, 14, 15, 16, 17, 18, 60]


def items_of_type(lst, the_type):
    return [x for x in lst if x.type == the_type]


def item_of_type(lst, the_type):
    items = items_of_type(lst, the_type)
    if len(items) != 1:
        raise RuntimeError("Bleh %d" % len(items))
    return items[0]


def plot(data, conds, channel):
    import matplotlib.pyplot as plt
    plt.figure()
    plt.title(channel)
    plt.plot(data)
    plt.legend([str(x) for x in conds])
    plt.figure()
    plt.title(channel)
    plt.imshow(data, interpolation="None")
    plt.colorbar()
    plt.show()


def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("path")
    parser.add_argument("-o, --outfile", dest="outfile", action="store_true", default=False)
    parser.add_argument("-p, --plot", dest="plot", action="store_true", default=False)
    parser.add_argument("channel", choices=["red", "green"])
    args = parser.parse_args()

    nf = nix.File.open(args.path, nix.FileMode.ReadOnly)
    neurons = [b for b in nf.blocks if b.type == 'neuron']

    if len(neurons) > 1:
        print("[W] More then one neuron in file, funny", file=sys.stderr)
        sys.exit(1)

    neuron = neurons[0]
    images = sorted(items_of_type(neuron.groups, "image.ca"),
                    key=lambda x: x.metadata['creation_time'])

    totalred = []
    totalgreen = []
    redconds = []
    for img in images:
        meta = img.metadata
        condition = meta['condition']
        loop = loops.get(condition, None)
        if loop is None:
            print("[W] %s: unknown loop. skipping" % condition, file=sys.stderr)
            continue

        das = img.data_arrays
        channels = item_of_type(das, "channel")
        red = list(np.nonzero(np.array(channels) == 1)[0])
        kymo = item_of_type(das, 'kymo.fg')
        data = kymo[:]
        l, t = data.shape
        allred = np.empty((l, len(red)))
        allgreen = np.empty((l, len(red)))
        cut = split_image(data)

        for i, r in enumerate(red):
            f0 = cut[i][0][:, 0:10].mean(axis=1)
            allred[:, i] = data[:, r]
            allgreen[:, i] = f0

        totalred.append(allred)
        totalgreen.append(allgreen)
        [redconds.append(l) for l in loop]

    #print(totalred)
    allred = np.hstack(totalred)
    allgreen = np.hstack(totalgreen)

    if args.channel == "red":
        alldata = allred
    else:
        alldata = allgreen

    filename = sys.stdout
    if args.outfile:
        bn = os.path.basename(args.path)
        name, ext = os.path.splitext(bn)
        filename = "%s.%s.csv" % (name, args.channel)

    #print(allred.shape)
    print("images:", [i.name for i in images], file=sys.stderr)
    print("conditions:", redconds, file=sys.stderr)
    if args.plot:
        plot(alldata, redconds, filename)

    df = pd.DataFrame(alldata)
    df.columns = [str(x) for x in redconds]
    df.to_csv(filename, index=False)

if __name__ == '__main__':
    main()

