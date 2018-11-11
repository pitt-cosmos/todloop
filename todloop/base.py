class TODLoop:
    """Main driving class for looping through coincident signals of different TODs"""
    def __init__(self):
        self._routines = []
        self._veto = False
        self._store = DataStore()  # initialize data store
        self._metadata = {}  # store metadata here
        self._tod_list = None
        self._tod_id = None
        self._tod_name = None
        self._skip_list = []

    def add_routine(self, routine):
        """Add a routine to the event loop"""
        self._routines.append(routine)
        print '[INFO] Added routine: %s' % routine.__class__.__name__
        routine.add_context(self)  # make event loop accessible in each routine

    def add_tod_list(self, tod_list_dir):
        """Add a list of TODs as input
        @par:
            tod_list_dir: string"""
        with open(tod_list_dir, "r") as f:
            self._tod_list = [line.split('\n')[0] for line in f.readlines()]
            self._metadata['list'] = self._tod_list

    def add_skip(self, skip_list):
        self._skip_list = skip_list

    def get_store(self):
        """Access the shared data storage"""
        return self._store
    
    def initialize(self):
        """Initialize all routines"""
        for routine in self._routines:
            routine.initialize()
    
    def execute(self):
        """Execute all routines"""
        for routine in self._routines:
            # check veto signal, if received, skip subsequent routines
            if self._veto:
                break
            else:
                routine.execute()
        self._veto = False
    
    def finalize(self):
        """Finalize all routines"""
        for routine in self._routines:
            routine.finalize()
    
    def run(self, start, end):
        """Main driver function to run the loop
        @param:
            start: starting tod_id
            end:   ending tod_id"""

        self.initialize()
        for tod_id in range(start, end):
            if tod_id in self._skip_list:
                print '[INFO] tod: %d in the skip_list, skipping ...' % tod_id
                continue  # skip if in skip list
            self._tod_id = tod_id
            self._tod_name = self._tod_list[tod_id]
            self.execute()

        self.finalize()
        
    def veto(self):
        """Veto a TOD from subsequent routines"""
        self._veto = True
    
    def get_id(self):
        """Return the index of current TOD in the list"""
        return self._tod_id

    def get_name(self):
        """Return name of the TOD"""
        # get metadata
        return self._tod_name

    def get_array(self):
        """Return name of the TOD"""
        # get metadata
        return self._tod_name.split('.')[-1]

    def add_metadata(self, key, obj):
        """Add a metadata, which will be saved together with the output
        to be used as reference for the future, for example, the list
        of TODs may be a reference for the future
        @par:
            key: string
            obj: any object
        """
        self._metadata[key] = obj

    def get_metadata(self, key=None):
        """Get metadata stored, by convention the list of TODs will
        be stored in the key metadata['list']"""
        if key:  # if a key is provided, return the metadata with the key
            if key in self._metadata:  # key exists
                return self._metadata[key]
            else:  # key doesn't exist
                return None
        else:  # if a key is not provided, return the entire metadata
            return self._metadata


class Routine:
    """A routine is a reusable unit of a particular algorithm,
    for example, it can be filtering algorithms that can be used
    in various studies."""
    def __init__(self):
        self._context = None

    def initialize(self):
        """Script that runs when the pipeline is initializing. It's
         a good place for scripts that need to run only once."""
        pass
    
    def execute(self):
        """Script that runs for each TOD"""
        pass
    
    def finalize(self):
        """Method that runs after all TODs have been processed. It's
        a good place to close opened files or connection if any."""
        pass
    
    def veto(self):
        """Prevent the TOD to be processed by other routines (stopped
        the pipeline for the TOD currently running. It's useful for
        filtering TODs"""
        self.get_context().veto()
        
    def add_context(self, context):
        """An internal function that's not to be called by users"""
        self._context = context
        
    def get_context(self):
        """Return the pipeline (event loop) that this routine is part of.
        This is useful because the pipeline contains a shared data store
        and metadata that may be useful"""
        return self._context

    def get_id(self):
        """A short cut to calling the get_id of parent pipeline"""
        return self.get_context().get_id()

    def get_store(self):
        """A short cut to calling the get_store of parent pipeline"""
        return self.get_context().get_store()

    def get_name(self):
        """A short cut to calling the get_name of parent pipeline"""
        return self.get_context().get_name()
    
    def get_array(self):
        tod_name = self.get_context().get_name()
        array_name = tod_name.split(".")[-2]
        return array_name 

class DataStore:
    """Cache class for event loop"""
    def __init__(self):
        self._store = {}
    
    def get(self, key):
        """Retrieve an object based on a key
        @par:
            key: str
        @ret:   
            Object of an arbitrary type associated with the key
            or None if no object is associated with the key"""
        if key in self._store:
            return self._store[key]
        else:
            return None
    
    def set(self, key, obj):
        """Save an object with a key
        @par:
            key: str
            obj: a object of arbitrary type
        @ret: nil"""
        self._store[key] = obj
