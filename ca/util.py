from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import numpy as np
from collections import defaultdict

def get_nb_condition(df):
    conds = np.unique(df.Condition)
    candidates = [x for x in conds if x.startswith("noise")]
    if len(candidates) > 0:
        return candidates[0]
    return candidates[0] if len(candidates) > 0 else "noisebox"


def load_exclude(path):
    import csv
    excludes = defaultdict(list)

    if path is None:
        return excludes

    with open(path, 'rb') as fd:
        ex = csv.reader(fd, delimiter=' ', quotechar='"')
        for row in ex:
            ncols = len(row)
            if ncols < 1:
                continue
            excludes[row[0]] += [{"image": row[1], "pulse": row[2]}]

    #for k, v in excludes.items():
    #    for ex in v:
    #       print('%s %s %s' % (k, ex['image'], ex['pulse']))

    return excludes
