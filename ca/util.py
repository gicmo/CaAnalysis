from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import numpy as np


def get_nb_condition(df):
    conds = np.unique(df.Condition)
    candidates = [x for x in conds if x.startswith("noise")]
    if len(candidates) > 0:
        return candidates[0]
    return candidates[0] if len(candidates) > 0 else "noisebox"
