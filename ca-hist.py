#!/usr/bin/env python
# coding=utf-8

from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import argparse
import itertools
import datetime
import nixio as nix
import numpy as np

from ca.nix import *

import matplotlib.pyplot as plt


def items_of_type(lst, the_type):
    return [x for x in lst if x.type == the_type]


def item_of_type(lst, the_type):
    items = items_of_type(lst, the_type)
    if len(items) != 1:
        raise RuntimeError("Bleh %d" % len(items))
    return items[0]


def analyse_image(image):
    das = image.data_arrays
    kymo = item_of_type(das, 'kymo.fg')
    return kymo.shape[0]


def analyse_neuron(neuron, args):
    meta = neuron.metadata
    age = meta['age']
    cond = meta['condition']

    if args.condition is not None and cond != args.condition:
        return None
    if args.age is not None and age != args.age:
        return None

    images = sorted(items_of_type(neuron.groups, "image.ca"),
                    key=lambda x: x.metadata['creation_time'])

    return [analyse_image(img) for img in images][0]


def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--bins", default=10)
    parser.add_argument("--condition", default=None)
    parser.add_argument("--age", default=None)
    parser.add_argument("path")
    args = parser.parse_args()

    filelist = find_files_recursive(args.path, "[!c]*.nix")

    lens = []
    for f in filelist:
        nf = nix.File.open(f, nix.FileMode.ReadOnly)

        neurons = [b for b in nf.blocks if b.type == 'neuron']
        if len(neurons) != 1:
            print("[W] More then one neuron in file, funny")

        lens += filter(lambda x: x is not None, [analyse_neuron(n, args) for n in neurons])

    print(lens)
    plt.hist(lens, bins=args.bins)
    age = args.age or "all"
    cond = args.condition or "all"
    plt.title("age: %s, condition: %s" % (age, cond))
    plt.show()


if __name__ == '__main__':
    main()

