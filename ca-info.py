#!/usr/bin/env python
# coding=utf-8

from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import argparse
import nixio as nix
import numpy as np


def items_of_type(lst, the_type):
    return [x for x in lst if x.type == the_type]


def item_of_type(lst, the_type):
    items = items_of_type(lst, the_type)
    if len(items) != 1:
        raise RuntimeError("Bleh %d" % len(items))
    return items[0]


def analyse_image(image, is_last):
    sign = u'└' if is_last else u'├'
    print(u"   %s─┮ %s" % (sign, image.name))
    das = image.data_arrays
    channels = item_of_type(das, "channel")
    red = list(np.nonzero(np.array(channels) == 1)[0])
    kymo = item_of_type(das, 'kymo.fg')
    sign = u' ' if is_last else u'│'
    print(u'   %s ├── kymo: %s' % (sign, str(kymo.shape)))
    print(u'   %s └── red: %s' % (sign, str(red)))


def get_marker(idx, count):
    if idx+1 == count:
        return u'└──'
    return u'├─'


def analyse_neuron(neuron):
    print(" " + neuron.name)
    meta = neuron.metadata
    props = { }

    if 'region' in meta:
        props['region'] = meta['region']
    if 'age' in meta:
        props['age'] = meta['age']
    if 'comment' in meta:
        props['comment'] = meta['comment']
    if 'condition' in meta:
        props['condition'] = meta['condition']

    images = sorted(items_of_type(neuron.groups, "image.ca"),
                    key=lambda x: x.metadata['creation_time'])

    for idx, (k, v) in enumerate(props.items()):
        sign = get_marker(idx, len(props)+len(images))
        print('   %s %s: %s' % (sign, k, v))

    for idx, img in enumerate(images):
        analyse_image(img, idx+1 == len(images))


def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("file")

    args = parser.parse_args()

    nf = nix.File.open(args.file, nix.FileMode.ReadOnly)

    neurons = [b for b in nf.blocks if b.type == 'neuron']
    if len(neurons) != 1:
        print("[W] More then one neuron in file, funny")

    for n in neurons:
        analyse_neuron(n)


if __name__ == '__main__':
    main()

