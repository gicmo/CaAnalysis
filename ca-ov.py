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

import matplotlib.pyplot as plt

from ca.nix import *
from ca.img import *
from ca.util import load_exclude

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
    plt.figure()
    plt.title(channel)
    plt.plot(data)
    plt.legend([str(x) for x in conds])
    plt.figure()
    plt.title(channel)
    plt.imshow(data, interpolation="None")
    plt.colorbar()
    plt.show()


def should_exclude_subimage(excludes, neuron, image, subimage):
    if neuron not in excludes:
        return False
    ex = excludes[neuron]
    for i in ex:
        if i['image'] == str(image) and i['pulse'] == str(subimage):
            return True
    return False

def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("path")
    parser.add_argument("-o, --outfile", dest="outfile", action="store_true", default=False)
    parser.add_argument("-p, --plot", dest="plot", action="store_true", default=False)
    parser.add_argument("channel", choices=["red", "green"])
    args = parser.parse_args()


    excludes = None
    ep = os.path.join(os.path.dirname(args.path), 'exludes.csv')
    if os.path.exists(ep):
        print("Using exludes.csv @ %s" % ep)
        excludes = load_exclude(ep)


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
    loopimg = {}
    for img in images:

        if should_exclude_subimage(excludes, neuron.name, img.name, "*"):
            print("Excluding %s *" % img.name)
            continue

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

        count = 0
        for i, r in enumerate(red):
            if i >= len(loop):
                continue
            if should_exclude_subimage(excludes, neuron.name, img.name, i+1):
                print("Excluding %s %d" % (img.name, i+1))
                continue

            f0 = cut[i][0][:, 0:10].mean(axis=1)
            allred[:, count] = data[:, r]
            allgreen[:, count] = f0
            count += 1
            lc = "ap%0.2d" % loop[i]
            if lc not in loopimg:
                loopimg[lc] = dff(cut[i][0], over=(None if args.channel == 'green' else data[:, r]))

        allred = allred[:, 0:count]
        allgreen = allgreen[:, 0:count]
        totalred.append(allred)
        totalgreen.append(allgreen)
        [redconds.append(l) for l in loop]
        print("count: %d" % count)
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
        filename = "%s.%s.pdf" % (name, args.channel)

    print("images:", [i.name for i in images], file=sys.stderr)
    print("conditions:", redconds, file=sys.stderr)

    plt.figure()

    ll = ["ap25", "ap03"]
    i = 0
    rows = (len(ll) / 2) + 1
    for i, c in enumerate(ll):
        ax = plt.subplot(rows, 2, 1+i)
        plt.imshow(loopimg[c], interpolation="None")
        plt.colorbar()
        ax.set_title(ll[i])
        plt.xlabel('time')

    ax = plt.subplot(rows, 2, i+2)
    plt.imshow(allgreen, interpolation="None")
    plt.colorbar()
    ax.set_title('green')
    plt.ylabel('dendrite')
    plt.xlabel('time')

    ax = plt.subplot(rows, 2, i+3)
    plt.imshow(allred, interpolation="None")
    plt.colorbar()
    ax.set_title('red')
    plt.ylabel('dendrite')
    plt.xlabel('time')


    if args.outfile:
        plt.savefig(filename)
    else:
        plt.show()


if __name__ == '__main__':
    main()

