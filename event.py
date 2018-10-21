from todloop.base import Routine
import moby2
# import moby2.scripting.products as products


class NPixelFilter(Routine):
    def __init__(self, min_pixels=0, max_pixels=100, input_key="events", output_key="events"):
        """Scripts that run during initialization of the routine"""
        Routine.__init__(self)
        self._min_pixels = min_pixels
        self._max_pixels = max_pixels
        self._input_key = input_key
        self._output_key = output_key
        self._events_passed = 0
        self._events_processed = 0

    def execute(self):
        """Scripts that run for each TOD"""
        events = self.get_store().get(self._input_key)
        events_filtered = [event for event in events if self._min_pixels <= len(event['pixels_affected']) < self._max_pixels]
        self._events_passed += len(events_filtered)
        self._events_processed += len(events)
        
        # if no events left, skip TOD
        if len(events_filtered) == 0:
            self.veto()  # skip subsequent routines
            return
        else:
            print '[INFO] Events passed %d / %d' % (len(events_filtered), len(events))
            self.get_store().set(self._output_key, events_filtered)
    
    def finalize(self):
        print '[INFO] Total events processed: %d' % self._events_processed
        print '[INFO] Total events passed: %d' % self._events_passed

        
class DurationFilter(Routine):
    def __init__(self, min_duration=1, max_duration=100, input_key="events", output_key="events"):
        """Scripts that run during initialization of the routine"""
        Routine.__init__(self)
        self._min_duration = min_duration
        self._max_duration = max_duration
        self._input_key = input_key
        self._output_key = output_key
        self._events_passed = 0
        self._events_processed = 0

    def execute(self):
        """Scripts that run for each TOD"""
        events = self.get_store().get(self._input_key)
        events_filtered = [event for event in events if self._min_duration <= event['duration'] < self._max_duration]
        self._events_passed += len(events_filtered)
        self._events_processed += len(events)
        
        # if no events left, skip TOD
        if len(events_filtered) == 0:
            self.veto()  # skip subsequent routines
            return
        else:
            print '[INFO] Events passed %d / %d' % (len(events_filtered), len(events))
            self.get_store().set(self._output_key, events_filtered)
    
    def finalize(self):
        print '[INFO] Total events processed: %d' % self._events_processed
        print '[INFO] Total events passed: %d' % self._events_passed
        

class CoeffFilter(Routine):
    def __init__(self, min_coeff=0.8, max_coeff=1, input_key="events", output_key="events"):
        """Filter events based on coefficient"""
        Routine.__init__(self)
        self._min_coeff = min_coeff
        self._max_coeff = max_coeff
        self._input_key = input_key
        self._output_key = output_key
        self._events_passed = 0
        self._events_processed = 0

    def execute(self):
        """Scripts that run for each TOD"""
        events = self.get_store().get(self._input_key)
        events_filtered = [event for event in events if self._min_coeff <= min(event['coefficients']) < self._max_coeff]
        self._events_passed += len(events_filtered)
        self._events_processed += len(events)

        # if no events left, skip TOD
        if len(events_filtered) == 0:
            self.veto()  # skip subsequent routines
            return
        else:
            print '[INFO] Events passed: %d / %d' % (len(events_filtered), len(events))
            self.get_store().set(self._output_key, events_filtered)
            
    def finalize(self):
        print '[INFO] Total events processed: %d' % self._events_processed
        print '[INFO] Total events passed: %d' % self._events_passed


class LoadRaDec(Routine):
    """A routine that loads the information about RA and DEC for each events"""
    def __init__(self, input_key="events", output_key="events"):
        Routine.__init__(self)
        self._event_key = input_key
        self._output_key = output_key

    def initialize(self):
        """Scripts that run before processing the first TOD"""
        user_config = moby2.util.get_user_config()
        moby2.pointing.set_bulletin_A(params=user_config.get('bulletin_A_settings'))

    def execute(self):
        """Scripts that run for each TOD"""
        events = self.get_store().get(self._event_key)

        new_events = []
        for event in events:  # loop over each event
            ra, dec = moby2.pointing.get_coords([event['ctime']], [event['az']], [event['alt']])
            event['ra'] = ra[0]  # ra / dec is a vector with one element
            event['dec'] = dec[0]
            new_events.append(event)

        self.get_store().set(self._output_key, new_events)
