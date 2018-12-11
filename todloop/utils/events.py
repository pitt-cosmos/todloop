import numpy as np


def timeseries(tod, pixel_id, s_time, e_time, pr, buffer=10,
               remove_mean=True):
    """return the time series associated with a given pixel and given
    start to end time 

    Args: 
        tod: tod data object
        pixel_id: pixel to plot
        s_time: start time 
        e_time: end time
        pr: PixelReader object for the given array and season
        buffer: buffer to add to the start time and end time
        remove_mean: if we want to remove the mean

    Return:
        ctime: reference time
        d1: time series from detector 1 (lower freq)
        d2: time series from detector 2 (lower freq)
        d3: time series from detector 3 (higher freq)
        d4: time series from detector 4 (higher freq)

    """
    # define start / end time with buffer
    start_time = max(s_time - buffer, 0)
    end_time = min(e_time + buffer, tod.data.shape[1])

    # get detectors corresponding to the pixel
    a1, a2 = pr.get_f1(pixel_id)
    b1, b2 = pr.get_f2(pixel_id)

    # get the time series associated with the detectors
    d1, d2 = tod.data[a1], tod.data[a2]
    d3, d4 = tod.data[b1], tod.data[b2]

    # extract the section of interests
    d_1 = d1[start_time:end_time]
    d_2 = d2[start_time:end_time]
    d_3 = d3[start_time:end_time]
    d_4 = d4[start_time:end_time]

    # remove the mean from start_time to end_time
    if remove_mean:
        d_1 -= np.mean(d_1)
        d_2 -= np.mean(d_2)
        d_3 -= np.mean(d_3)
        d_4 -= np.mean(d_4)

    # get reference ctime
    ctime = tod.ctime - tod.ctime[0]
    ctime = ctime[start_time:end_time]

    return ctime, d_1, d_2, d_3, d_4


# unused
def energy_calculator(pid, stime, etime):
    all_amps = []
    all_amps.append(timeseries(pid,stime,etime,buffer=0)[1])
    all_amps.append(timeseries(pid,stime,etime,buffer=0)[2])
    all_amps.append(timeseries(pid,stime,etime,buffer=0)[3])
    all_amps.append(timeseries(pid,stime,etime,buffer=0)[4])

    pJ_90a, pJ_90b, pJ_150a, pJ_150b = [],[],[],[]

    for i in range(0,len(all_amps),4):
        amp_90a,amp_90b,amp_150a,amp_150b = all_amps[i],all_amps[i+1],all_amps[i+2],all_amps[i+3]
        norm_90a,norm_90b,norm_150a,norm_150b = amp_90a-np.amin(amp_90a),amp_90b-np.amin(amp_90b),amp_150a-np.amin(amp_150a),amp_150b-np.amin(amp_150b)
        pJ_90a.append((etime-stime)*np.sum(norm_90a)*10**(12)/(400.))
        pJ_90b.append((etime-stime)*np.sum(norm_90b)*10**(12)/(400.))
        pJ_150a.append((etime-stime)*np.sum(norm_150a)*10**(12)/(400.))
        pJ_150b.append((etime-stime)*np.sum(norm_150b)*10**(12)/(400.))

    """Returns the total energy of the pixel (sum of 4 detectors)"""
    return np.sum(pJ_90a) + np.sum(pJ_90b) + np.sum(pJ_150a) + np.sum(pJ_150b)


def find_peaks(hist):
    """Find peaks in the histogram corresponding to physical events
    :param hist: histogram of coincident signals
    :return: list of peaks with [start_time, end_time, duration, n_pixels_affected]
    """
    last = 0
    peaks = []
    for i in range(len(hist)):
        if hist[i] > 0 and last == 0:
            peak_start = i
        if hist[i] == 0 and last > 0:
            peak_end = i
            peak_amp = max(hist[peak_start:peak_end])
            duration = peak_end - peak_start
            peaks.append([peak_start, peak_end, duration, peak_amp])
        last = hist[i]
    return peaks
