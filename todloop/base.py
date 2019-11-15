import gc, os, numpy as np

import logging
logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')

class TODLoop:
    """Main driving class for looping through coincident signals of different TODs"""
    def __init__(self):
        self._routines = []
        self._veto = False
        self._metadata = {}  # store metadata here
        self._tod_list = None
        self._skip_list = []
        self._error_list = []
        self._tod_id = None
        self._tod_name = None
        self._fb = None
        self._abspath = False
        self.comm = None
        self.rank = 0
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)

    def add_routine(self, routine):
        """Add a routine to the event loop"""
        self._routines.append(routine)
        self.logger.info('Added routine: %s' % routine.__class__.__name__)
        routine.add_context(self)  # make event loop accessible in each routine

    def add_tod_list(self, tod_list_dir, abspath=False):
        """Add a list of TODs as input
        @par:
            tod_list_dir: string
            abspath: bool - if tod name is given in absolute path or not"""
        with open(tod_list_dir, "r") as f:
            self._tod_list = [line.split('\n')[0] for line in f.readlines()]
            self._metadata['list'] = self._tod_list

        # set abspath flag
        self._abspath = abspath

    def add_skip(self, skip_list):
        self._skip_list = skip_list

    def initialize(self):
        """Initialize all routines"""
        for routine in self._routines:
            routine.initialize()

    def execute(self, store):
        """Execute all routines"""
        for routine in self._routines:
            # check veto signal, if received, skip subsequent routines
            if self._veto:
                break
            else:
                routine.execute(store)

        self._veto = False

    def finalize(self):
        """Finalize all routines"""
        for routine in self._routines:
            routine.finalize()

    def run(self, start=0, end=None):
        """Main driver function to run the loop
        @param:
            start: starting tod_id (default 0)
            end:   ending tod_id (default None)"""

        self.initialize()
        # if end is not provided, run all
        if not end:
            end = len(self._tod_list)
        for tod_id in range(start, end):
            self.logger.info('TOD ID: %d' % tod_id)
            if tod_id in self._skip_list:
                self.logger.info('TOD: %d in the skip_list, skipping ...' % tod_id)
                continue  # skip if in skip list
            self._tod_id = tod_id
            self._tod_name = self._tod_list[tod_id]
            self.logger.info("TOD ID %d: %s" % (tod_id, self._tod_name))

            # initialize data store
            store = DataStore()
            try:
                self.execute(store)
            except Exception as e:
                self.logger.error("%s occurred, skipping..." % type(e))
                self._error_list.append(self._tod_name)

            # clean memory
            gc.collect()

        self.finalize()

    def run_parallel(self, n_workers=1):
        n_total = len(self._tod_list)
        self.logger.info("Distributing %d tods to %d workers" % \
                         (n_total, n_workers))
        # setup mpi
        from mpi4py import MPI
        comm = MPI.COMM_WORLD
        size = comm.Get_size()
        rank = comm.Get_rank()
        self.comm = comm
        self.rank = rank
        self.logger.info("Node @ rank=%d\t size=%d" % (rank, size))
        # distribute tasks
        tasks = np.array_split(range(n_total), n_workers)
        start = tasks[rank][0]
        end = task[rank][1]+1
        self.run(start=start, end=end)

    def veto(self):
        """Veto a TOD from subsequent routines"""
        self._veto = True

    def get_id(self):
        """Return the index of current TOD in the list"""
        return self._tod_id

    def get_name(self):
        """Return name of the TOD"""
        # get metadata
        if self._abspath:
            return os.path.basename(self._tod_name)
        else:
            return self._tod_name

    def get_filename(self):
        # check if we are looking at abspath or not
        if self._abspath:
            return self._tod_name
        else:
            # check if filebase is setup
            if self._fb:
                return self._fb.filename_from_name(self.get_name(), single=True)
            else:
                from moby2.scripting import get_filebase
                self._fb = get_filebase()
                return self._fb.filename_from_name(self.get_name(), single=True)

    def get_array(self):
        """Return name of the TOD"""
        # get metadata
        fields = self._tod_name.split('.')
        if 'ar' in fields[-1].lower():
            return fields[-1]
        else:  # end with zip
            return fields[-2]

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
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)

    def initialize(self):
        """Script that runs when the pipeline is initializing. It's
         a good place for scripts that need to run only once."""
        pass

    def execute(self, store):
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
        self.logger.info("TOD vetod, skipping subsequent routines...")
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

    def get_comm(self):
        return self.get_context().comm

    def get_rank(self):
        return self.get_context().rank

    def get_filename(self):
        return self.get_context().get_filename()

    def get_array(self):
        tod_name = self.get_context().get_name()
        array_name = tod_name.split(".")[-2]
        return array_name


class DataStore:
    """Cache class for event loop"""
    def __init__(self):
        self._store = {}

    def get(self, key, default=None):
        """Retrieve an object based on a key
        @par:
            key: str
        @ret:
            Object of an arbitrary type associated with the key
            or None if no object is associated with the key"""
        if key in self._store:
            return self._store[key]
        else:
            return default

    def set(self, key, obj):
        """Save an object with a key
        @par:
            key: str
            obj: a object of arbitrary type
        @ret: nil"""
        self._store[key] = obj
