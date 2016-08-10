#!/usr/bin/env python
# coding=utf-8

from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import argparse

import datetime
import nixio as nix
import numpy as np

from ca.nix import *


def check_metadata(neuron, args):
    fields = ['age', 'condition', 'subregion']

    meta = neuron.metadata
    for f in fields:
        if f not in meta:
            yield "'%s' missing" % f

    if "condition" in meta and meta["condition"] == "Noisebox":
        if 'litter' not in meta:
            yield "'litter' missing"


def check_neuron(neuron, args):
    warns = [f for f in check_metadata(neuron, args)]

    if len(warns) > 0:
        print("neuron: %s\n  %s" % (neuron.name, "\n  ".join(warns)))


def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("path")
    args = parser.parse_args()

    filelist = find_files_recursive(args.path, "[!c]*.nix")

    for f in filelist:
        nf = nix.File.open(f, nix.FileMode.ReadOnly)

        neurons = [b for b in nf.blocks if b.type == 'neuron']
        if len(neurons) != 1:
            print("[W] More then one neuron in file, funny")

        for n in neurons:
            check_neuron(n, args)


if __name__ == '__main__':
    main()
