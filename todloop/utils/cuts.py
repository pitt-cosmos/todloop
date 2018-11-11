import numpy as np
import moby2


def merge_cuts(cut1, cut2):
    """Merge two cutvectors
    input cuts have to be CutVector type"""
    if len(cut1) == 0:
        return cut2
    if len(cut2) == 0:
        return cut1

    nsamps = max(cut1[-1][1], cut2[-1][1])
    c1m = cut1.get_mask(nsamps=nsamps)
    c2m = cut2.get_mask(nsamps=nsamps)
    cm = np.logical_or(c1m, c2m)
    merged = moby2.tod.CutsVector.from_mask(mask=cm)
    return merged


def common_cuts(cut1, cut2):
    """Find common cuts from two cuts
    Input cuts must be of CutVectors type"""
    if len(cut1) == 0:
        return cut1
    if len(cut2) == 0:
        return cut2
    nsamps = max(cut1[-1][1], cut2[-1][1])
    c1m = cut1.get_mask(nsamps=nsamps)
    c2m = cut2.get_mask(nsamps=nsamps)
    cm = np.logical_and(c1m, c2m)
    common = moby2.tod.CutsVector.from_mask(mask=cm)
    return common


def remove_overlap_vector(original, to_remove, buff=0):
    """remove the to_remove CutVector from original CutVector"""
    for row in to_remove:
        original = original[(original[:, 1]<row[0]-buff) | (original[:, 0]>row[1]+buff)]
    return original


def remove_overlap_tod(original, to_remove, buff=0):
    """remove the to_remove TODCuts from original TODCuts"""
    ndet = len(original.cuts)
    for i in range(ndet):
        # loop over detector
        original.cuts[i] = remove_overlap_vector(original.cuts[i], to_remove.cuts[i], buff)
    return original


def trim_edge_cuts(cuts, nsamps):
    """remove edge cuts, cuts covering first/last THRES sampling points are removed"""
    thres = 100 # sampling points
    for i in range(len(cuts.cuts)):
        cuts.cuts[i] = cuts.cuts[i][(cuts.cuts[i][:, 0] > thres) & (cuts.cuts[i][:, 1] < (nsamps-thres))]
    return cuts


def cut_contains(cv, v):
    """check if a specific time is cut in a det (provided CutVector)"""
    for c in cv:
        if c[0] <= v <= c[1]:
            return True
    return False


def pixels_affected(cs, v):
    return [int(p) for p in cs if cut_contains(cs[p], v)]


def pixels_affected_in_event(cs, event):
    pixels_affected_list = []
    start_time = event[0]
    end_time = event[1]
    for t in range(start_time, end_time):
        pixels_affected_list.extend(pixels_affected(cs,t))

    return list(set(pixels_affected_list))

