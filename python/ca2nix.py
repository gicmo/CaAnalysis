#!/usr/bin/env python
from __future__ import print_function
import os

import h5py as h5
import nix
import argparse
import datetime
import numpy as np


def is_nix_file(path):
    try:
        nf = h5.File(path, mode='r')
    except IOError:
        return False
    return 'format' in nf.attrs and nf.attrs['format'] == 'nix'


def find_type(parent, type_to_find):
    def is_of_type(group):
        return 'type' in group.attrs and group.attrs['type'] == type_to_find

    return [group for _, group in parent.iteritems() if is_of_type(group)]


def find_neurons(nf):
    return find_type(nf, 'neuron')


def find_images(neuron):
    return find_type(neuron, 'image')


def is_ca_file(path):
    try:
        nf = h5.File(path, mode='r')
        return len(find_neurons(nf)) != 0
    except IOError:
        return False

def convert_ca_file(path):
    root, ext = os.path.splitext(path)
    h5fd = h5.File(path, mode='r')
    nix_path = "%s.nix.h5" % root
    nifd = nix.File.open(nix_path, nix.FileMode.Overwrite)

    neurons = find_neurons(h5fd)
    for neuron in neurons:
        name = neuron.name[1:]
        print("   - neuron: %s" % name)

        block = nifd.create_block(str(name), 'ca.neuron')
        images = find_images(neuron)
        images = sorted(images, key=lambda x: int(x.name[len(neuron.name)+1:]))
        for img in images:
            img_name = img.name[len(neuron.name)+1:]
            ctime = img.attrs['ctime']
            dt = datetime.datetime.fromtimestamp(ctime / 1000.0)
            dt_str = dt.strftime("%A, %d. %B %Y %I:%M%p")
            print("   |- image: %3s  %s [%s]" % (img_name, dt_str, ctime))
            subgroups = ['kymoFg', 'kymoBg', 'roiFg', 'roiBg']
            typemap = {
                'kymoFg': 'ca.kymo.fg',
                'kymoBg': 'ca.kymo.bg',
                'roiFg': 'ca.roi.fg',
                'roiBg': 'ca.roi.bg'
            }

            for sg in subgroups:
                ds = img[sg]
                data = np.array(ds)
                ds_name = ds.name[len(img.name)+1:]
                print("   | |- %s %s [%s]" % (ds_name, str(data.shape), str(data.dtype)))

                da_name = '%s.%s' % (img_name, sg)
                block.create_data_array(str(da_name), typemap[sg], data=data)

            print("   |  ")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert old CaManager files to nix')
    parser.add_argument('files', nargs='+', default=None)
    args = parser.parse_args()

    for f in args.files:
        if is_nix_file(f):
            print('%s is in nix format already' % f)
        elif is_ca_file(f):
            print('Found CaManager file: %s' %f)
            convert_ca_file(f)


