from todloop.base import Routine
import numpy as np


class Filter(Routine):
    def __init__(self, input_key, output_key):
        Routine.__init__(self)
        self._input_key = input_key
        self._output_key = output_key


class DurationFilter(Filter):
    """An event filter based on the duration of events (set max duration)"""
    def __init__(self, max_duration=50, input_key='data', output_key='data'):
        Filter.__init__(self, input_key=input_key, output_key=output_key)
        self._max_duration = max_duration
        
    def execute(self):
        cosig = self.get_context().get_store().get(self._input_key)
        peaks = cosig['peaks']
        print '[INFO] Before: n_tracks = %d' % len(cosig['peaks'])
        peaks_filtered = [peak for peak in peaks if peak[2] < self._max_duration]
        cosig['peaks'] = peaks_filtered
        print '[INFO] After: n_tracks = %d' % len(cosig['peaks'])
        if len(cosig['peaks']) == 0:
            self.veto()  # stop subsequent routines
        self.get_context().get_store().set(self._output_key, cosig)
        
        
class PixelFilter(Filter):
    """An event filter based on the number of pixels affected (set max n_pixels)"""
    def __init__(self, max_pixels=10, input_key='data', output_key='data'):
        Filter.__init__(self, input_key, output_key)
        self._max_pixels = max_pixels
        
    def execute(self):
        cosig = self.get_context().get_store().get(self._input_key)
        peaks = cosig['peaks']
        print '[INFO] Before: n_tracks = %d' % len(cosig['peaks'])
        peaks_filtered = [peak for peak in peaks if peak[3] < self._max_pixels]
        cosig['peaks'] = peaks_filtered
        print '[INFO] After: n_tracks = %d' % len(cosig['peaks'])
        self.get_context().get_store().set(self._output_key, cosig)

        
class SpreadFilter(Filter):
    """A track filter based on the mean spread of the tracks (set max spread).
       Dependency: [ GetTracks ]"""
    def __init__(self, max_spread=10, input_key='tracks', output_key='tracks'):
        Filter.__init__(self, input_key, output_key)
        self._max_spread = max_spread
        
    def execute(self):
        tracks = self.get_context().get_store().get(self._input_key)
        print '[INFO] Before: n_tracks = %d' % len(tracks)
        # filter based on mean spread
        tracks_new = [track for track in tracks if np.mean(track[:, 2]) < self._max_spread]
        print '[INFO] After: n_tracks = %d' % len(tracks_new)
        self.get_context().get_store().set(self._output_key, tracks_new)


class NCosigFilter(Filter):
    """A TOD filter based on the number of cosig (coincident signals)
       (set max n_cosig)"""
    def __init__(self, max_cosig=100, input_key='data', output_key='data'):
        Filter.__init__(self, input_key, output_key)
        self._max_cosig = max_cosig

    def execute(self):
        cosig = self.get_context().get_store().get(self._input_key)
        peaks = cosig['peaks']
        if len(peaks) > self._max_cosig:
            self.veto()  # halt subsequent routines


class TrackLengthFilter(Filter):
    """A track filter that select tracks up to a maximum lengths"""
    def __init__(self, max_length=100, input_key="tracks", output_key="tracks"):
        Routine.__init__(self, input_key, output_key)
        self._max_length = max_length

    def execute(self):
        tracks = self.get_context().get_store().get(self._input_key)
        # filter tracks based on the length of tracks
        tracks_new = [track for track in tracks if len(tracks) < self._max_length]
        self.get_context().get_store().set(self._output_key, tracks_new)
