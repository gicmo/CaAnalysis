#!/usr/bin/env python
# coding=utf-8

from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os
import fnmatch
import argparse

import datetime
from collections import defaultdict

import nixio as nix
import numpy as np

from ca.nix import *
from ca.img import *


loops = {
    "1": [3,  1, 10, 1],
    "2": [3,  1, 25, 3],
    "3": [1, 25,  3, 1, 10]
}

pulses = [1, 3, 10, 25]


def find_files_recursive(dir, glob):
    entries = os.listdir(dir)
    res = []
    for e in entries:
        fn = os.path.join(dir, e)
        if os.path.isdir(fn):
            res += find_files_recursive(fn, glob)
        elif fnmatch.fnmatch(e, glob):
            res += [fn]
    res = map(os.path.abspath, res)
    return res


def valid_column(row, colid):
    if not (colid < len(row)):
        return False
    col = row[colid].strip()
    return len(col) > 0 and not col.startswith("#")


def load_exclude(path):
    import csv
    excludes = {}

    if path is None:
        return excludes

    with open(path, 'rb') as fd:
        ex = csv.reader(fd, delimiter=' ', quotechar='"')
        for row in ex:
            ncols = len(row)
            if ncols < 1:
                continue
            excludes[row[0]] = {
                "image": row[1] if valid_column(row, 1) else "*",
                "pulse": row[2] if valid_column(row, 2) else "*"
            }
    return excludes


class CaAnalyser(object):
    def __init__(self, root, over, condition, age, excludes=None):
        self.root = root
        self.condition = condition
        self.age = age
        self.excludes = excludes or {}
        self.filelist = None
        self.bsl = 10 # baselinesize
        self.over = over
        # NIX outfile related things
        self.nf = None
        self.dff_full = None
        self.dff_mean = None
        self.dff_peak = None
        self.peaks = None
        # Current processing state
        self.neuron = None
        self.image = None
        self.idx = 0
        self.loop = None

    def setup(self):
        self.filelist = find_files_recursive(self.root, "[!c]*.nix")
        if len(self.filelist) == 0:
            return
        outname = "ca-%s-P%s-%s.nix" % (self.condition, self.age, self.over)
        self.nf = nix.File.open(outname, nix.FileMode.Overwrite)
        self.dff_full = self.nf.create_block("full", "dff.full")
        self.dff_mean = self.nf.create_block("mean", "dff.mean")
        self.dff_peak = self.nf.create_block("peak", "dff.peak")

        b = self.dff_peak
        self.peaks = [b.create_data_array("ap%d.all" % p, "pulse.%d.max" % p,
                                          dtype='d', shape=(0, 2)) for p in pulses]
        for da in self.peaks:
            da.append_set_dimension()
            da.append_set_dimension()

    def process(self):
        for path in self.filelist:
            self.process_file(path)

    def process_file(self, path):
        cf = nix.File.open(path, nix.FileMode.ReadOnly)
        neurons = [b for b in cf.blocks if b.type == 'neuron']

        for neuron in neurons:
            name = neuron.name
            meta = neuron.metadata

            nc = meta["condition"].lower() if "condition" in meta else ""
            age = meta["age"].lower() if "age" in meta else ""

            exclude = self.excludes.get(name, {"image": None})["image"] == "*"
            msg = name
            if exclude:
                msg += " skipping (exclude file)"
            elif nc != self.condition:
                exclude = True
                msg += " skipping (wrong condition)"
            elif age != self.age:
                exclude = True
                msg += " skipping (wrong age)"

            msg = (u'├── ' if exclude else u'├─┬ ' ) + msg
            print(msg)
            if exclude:
                continue

            self.process_neuron(neuron)

        cf.close()

    def process_neuron(self, neuron):
        self.neuron = neuron

        images = sorted(items_of_type(neuron.groups, "image.ca"),
                        key=lambda x: x.metadata['creation_time'])

        pos_loop = defaultdict(list)
        for image in images:
            pos = self.process_image(image)
            for l, p in pos.items():
                pos_loop[l] += p

        print(u'│ ├─ Tags: ', end='')
        dff_peak = self.dff_peak
        for l, p in pos_loop.items():
            print("ap%d " % l, end='')
            pdat = np.zeros((len(p), 2))
            pdat[:, 0] = p
            aps = "ap%d" % l
            name = "%s.%s" % (self.neuron.name, aps)
            pos = dff_peak.create_data_array(name + ".pos", "nix.positions", data=pdat)
            pos.append_set_dimension()
            pos.append_set_dimension()
            mtag = self.dff_peak.create_multi_tag(name, aps, pos)
            mtag.references.append(self.peaks[pulses.index(l)])
            data = np.array([mtag.retrieve_data(pc, 0)[0] for pc in range(len(p))])
            avg = dff_peak.create_data_array(name + ".avg", "pulse.%d.max.avg" % l, data=data.mean())
            mtag.create_feature(avg, nix.LinkType.Untagged)
            # TODO: dimensions, metadata

        print('')

    def process_image(self, image):
        self.image = image

        meta = image.metadata
        das = image.data_arrays
        channels = item_of_type(das, "channel")
        red = list(np.nonzero(np.array(channels) == 1)[0])
        kymo = item_of_type(das, 'kymo.fg')
        condition = meta['condition']
        loop = loops.get(condition, None)
        if loop is None:
            print(u'│ ├──  WARN: unknown loop: %s. skipping!' % condition)
            return
        else:
            print(u'│ ├── image: %s, Loop: %s' % (image.name, condition), end='')
        if len(loop) != len(red):
            print(' [len(loops) != len(condition)]', end='')


        imgs = split_image(kymo[:])
        self.loop = loop

        pos_loop = defaultdict(list)

        print(" [", end='')
        for idx, l in enumerate(loop):
            print('%2d; ' % self.loop[idx], end='')
            img = imgs[idx]

            over_data = img[1] if self.over == 'red' else None
            dff_data = dff(img[0], over_data, baseline=self.bsl)

            di = self.save_dff_full(idx, data=dff_data)
            # TODO: metadata

            dff_mean = np.array(dff_data).mean(axis=0)
            da_mean = self.save_dff_mean(idx, data=dff_mean)

            peak_idx = np.argmax(dff_mean)
            peak_val = dff_mean[peak_idx]

            da_peaks = self.peaks[pulses.index(l)]

            pos_loop[l] += [da_peaks.shape[0]]
            da_peaks.append(np.array([peak_val, peak_idx]).reshape((1, 2)), axis=0)

        print('] ')
        return pos_loop

    def finish(self):
        if self.nf is not None:
            self.dff_full = None
            self.dff_mean = None
            self.nf.close()

    def save_dff_full(self, idx, data):
        suffix = self.over
        da_name = "%s.%s.%d.%s" % (self.neuron.name, self.image.name, idx+1, suffix)
        da_type = "dff." + suffix
        da = self.dff_full.create_data_array(da_name, da_type, data=data)
        da.label = 'dF/F (%s)' % suffix

        dim = da.append_sampled_dimension(1)
        dim.label = 'location'

        dim = da.append_sampled_dimension(30)
        dim.label = 'time'
        dim.unit = 'ms'
        # TODO: offset

        return da

    def save_dff_mean(self, idx, data):
        suffix = self.over
        da_name = "%s.%s.%d.%s" % (self.neuron.name, self.image.name, idx+1, suffix)
        da_type = "dff.mean." + suffix
        da = self.dff_mean.create_data_array(da_name, da_type, data=data)
        da.label = 'mean dF/F (%s)' % suffix

        dim = da.append_set_dimension()
        dim.label = 'location'

        dim = da.append_sampled_dimension(30)
        dim.label = 'time'
        dim.unit = 'ms'
        # TODO: offset

        return da


def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("root")
    parser.add_argument("over", choices=["red", "green"])
    parser.add_argument("condition", choices=['noisebox', 'control'])
    parser.add_argument("age", choices=["10", "11", "13", "14", "15", "16", "17", "18", "60"])
    parser.add_argument("--exclude", type=str, default=None)

    args = parser.parse_args()
    excludes = load_exclude(args.exclude)

    analyser = CaAnalyser(args.root, args.over, args.condition, args.age, excludes)
    analyser.setup()
    analyser.process()
    analyser.finish()

if __name__ == '__main__':
    main()
