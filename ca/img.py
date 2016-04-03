# coding=utf-8

import numpy as np


def dff(data, df=None, baseline=10):
    l = data.shape[0]
    t = data.shape[1]

    if df is None:
        df = data[:, 0:baseline].mean(axis=1).reshape((l, 1))

    df = np.tile(df, (1, t))

    return (data - df) / df


def split_image(data, n=91):
    nimg = data.shape[1] / n
    slices = [np.s_[i*n:(i+1)*n] for i in range(nimg)]

    def split_red(img):
        return img[:, 0:n-1], img[:, n-1].reshape(data.shape[0], 1)

    return map(split_red, [data[:, s] for s in slices])