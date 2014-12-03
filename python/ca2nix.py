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


def convert_data_generic(dset, block):
    pr_name = os.path.basename(dset.parent.name)
    data = np.array(dset)
    ds_name = os.path.basename(dset.name).lower()
    da_name = "%s.%s" % (pr_name, ds_name)
    da_type = "%s.%s" % (ds_name[-2:], ds_name[:-1])
    da = block.create_data_array(str(da_name), str(da_type), data=data)
    print("   | |- %s %s [%s]" % (da_name, str(data.shape), str(data.dtype)))
    return da


def convert_kymo(dset, block):
    da = convert_data_generic(dset, block)
    da.label = 'fluorescent'

    dim = da.append_sampled_dimension(30)
    dim.unit = "ms"
    dim.label = "time"
    #fixme: add global offset? dim.offset = 0.0

    dim = da.append_sampled_dimension(1)
    dim.label = 'location'


def convert_roi(dset, block):
    da = convert_data_generic(dset, block)


def convert_image(img, block):
    img_name = os.path.basename(img.name)
    ctime = img.attrs['ctime']
    dt = datetime.datetime.fromtimestamp(ctime / 1000.0)
    dt_str = dt.strftime("%A, %d. %B %Y %I:%M%p")
    print("   |- image: %3s  %s [%s]" % (img_name, dt_str, ctime))
    typemap = {
        'kymoFg': convert_kymo,
        'kymoBg': convert_kymo,
        'roiFg': convert_roi,
        'roiBg': convert_roi
    }

    for name, cfunc in typemap.iteritems():
        cfunc(img[name], block)

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
            convert_image(img, block)
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


