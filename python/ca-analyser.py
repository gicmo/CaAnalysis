#!/usr/bin/env python
from __future__ import print_function
import os
import sys

import nix
import argparse
import numpy as np

import matplotlib.pyplot as plt


def deltafoverf(data, F=None):
    l = data.shape[0]
    t = data.shape[1]

    if F is None:
        F = data[:, 0:10].mean(axis=1).reshape((l, 1))

    F = np.tile(F, (1, t))

    return (data - F) / F


def split_image(data):
    n = 91
    nimg = data.shape[1] / n
    slices = [np.s_[i*n:(i+1)*n] for i in range(nimg)]

    def split_red(img):
        return img[:, 0:n-1], img[:, n-1].reshape(data.shape[0], 1)

    return map(split_red, [data[:, s] for s in slices])


def pharma_dff(block, name, data, F=None):
    suffix = 'green' if F is None else 'red'
    dff = deltafoverf(data, F)
    dff_mean = dff.mean(axis=0)
    da = block.create_data_array(name + '.' + suffix, 'dff', data=dff)
    da.label = 'dF/F'

    dim = da.append_sampled_dimension(1)
    dim.label = 'location'

    dim = da.append_sampled_dimension(30)
    dim.label = 'time'
    dim.unit = 'ms'

    da = block.create_data_array(name + '.' + suffix + '.mean', 'dff.mean', data=dff_mean)
    dim = da.append_sampled_dimension(30)
    dim.label = 'time'
    dim.unit = 'ms'

    dim = da.append_set_dimension()

    return da


def pharma_image(block, image):
    img_index = image.metadata['ImageIndex']
    data = np.array(image)
    print(' [I] %d %s -  %s' % (img_index, image.name, str(data.shape)), file=sys.stderr)
    ts = image.dimensions[1].sampling_interval
    images = split_image(data)

    conditions = ['AP3', 'AP10', 'AP25']

    for i, c in enumerate(conditions):
        name = '%d.%s' % (img_index, c)
        pharma_dff(block, name, images[i][0])
        pharma_dff(block, name, images[i][0], images[1][1])

    #plt.plot(dff_mean)
    #plt.show()
    #print(dff)


def pharmacology_analysis(nf, neuron):
    date = neuron.name

    ba_name = '%s.analysis' % neuron.name
    ba = nf.create_block(ba_name, 'ca.analysis')

    print('[A] %s - %s' % (neuron.name, date), file=sys.stderr)
    images = [fg for fg in neuron.data_arrays if fg.type.endswith('kymo.fg')]
    images = sorted(images, key=lambda x: int(x.name.split('.')[0]))
    [pharma_image(ba, img) for img in images]


supported_analysis = {
    'pharmacology': pharmacology_analysis
}


def main(args):
    nf = nix.File.open(args.file, nix.FileMode.ReadWrite)
    neurons = [b for b in nf.blocks if b.type == 'ca.neuron']

    def do_ana(block):
        etype = block.metadata['Type']
        if etype not in supported_analysis:
            print('Analysis for %s not supported [%s]. Skipping!' % (block.name, etype))
            return
        func = supported_analysis[etype]
        func(nf, block)

    [do_ana(n) for n in neurons]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Perform analysis of Ca data')
    parser.add_argument('file')
    args = parser.parse_args()
    main(args)