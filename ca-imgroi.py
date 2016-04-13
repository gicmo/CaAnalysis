#!/usr/bin/env python
from __future__ import print_function

import itertools
import os
import sys
import numpy as np
import PIL.Image
import PIL.TiffImagePlugin
import matplotlib.pyplot as plt
import matplotlib
import nixio as nix

if sys.byteorder == 'little':
    _ENDIAN = '<'
else:
    _ENDIAN = '>'

DTYPES = {
          "1": ('|b1', None),
          "L": ('|u1', None),
          "I": ('%si4' % _ENDIAN, None),
          "F": ('%sf4' % _ENDIAN, None),
          "I;16": ('%su2' % _ENDIAN, None),
          "I;16B": ('%su2' % _ENDIAN, None),
          "I;16S": ('%si2' % _ENDIAN, None),
          "P": ('|u1', None),
          "RGB": ('|u1', 3),
          "RGBX": ('|u1', 4),
          "RGBA": ('|u1', 4),
          "CMYK": ('|u1', 4),
          "YCbCr": ('|u1', 4),
          }


def stack_len(img):
    for i in itertools.count():
        try:
            img.seek(i)
        except EOFError:
            return i


def load_data(img):
    try:
        dtype, extra = DTYPES[img.mode]
    except KeyError:
        raise RuntimeError("%s mode is not supported" % img.mode)
    shape = (img.size[1], img.size[0])
    if extra is not None:
        shape += (extra,)
    try:
        return np.array(img, dtype=np.dtype(dtype)).reshape(shape)
    except SystemError:
        return np.array(img.getdata(), dtype=np.dtype(dtype)).reshape(shape)


def load_stack(img):
    zlen = stack_len(img)
    try:
        dtype, extra = DTYPES[img.mode]
    except KeyError:
        raise RuntimeError("%s mode is not supported" % img.mode)
    shape = (zlen, img.size[1], img.size[0])
    stack = np.empty(shape, dtype=np.dtype(dtype))
    for i in range(zlen):
        img.seek(i)
        stack[i, :, :] = np.array(img, dtype=np.dtype(dtype)).reshape((img.size[1], img.size[0]))
    return stack


def main():
    import argparse

    parser = argparse.ArgumentParser(description='CaAnalyser - Plot Image+ROI')
    parser.add_argument('path')
    parser.add_argument('image')
    args = parser.parse_args()

    name = os.path.basename(args.path)
    nf = nix.File.open(os.path.join(args.path, name + '.nix'), nix.FileMode.ReadOnly)
    block = nf.blocks[name]

    meta = nf.sections[name]
    im = meta[args.image]
    filename = im['filename']
    print(filename)

    roi = block.data_arrays['%s.roi.xy.fg' % args.image]
    rdata = roi[:]

    PIL.TiffImagePlugin.OPEN_INFO[(PIL.TiffImagePlugin.II,
                                   0, 1, 1, (16,), ())] = ("I;16", "I;16")
    img = PIL.Image.open(os.path.join(args.path, filename))
    print(img.mode)
    x = stack_len(img)
    data = load_stack(img)
    print(data.shape)
    plt.imshow(data[0, :, :], cmap="gray", interpolation=None)

    plt.scatter(rdata[0, :], rdata[1, :], s=2, color='red')

    for k, i in enumerate(zip(rdata[0, :], rdata[1, :])):
        if k % 10 != 0:
            continue
        x, y = i[0], i[1]
        plt.gca().annotate("%d" % k, (x, y), color='yellow', fontsize=10)

    plt.show()

if __name__ == "__main__":
    main()
