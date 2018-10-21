import os
from todloop.base import Routine
import cPickle
import pprint


class OutputRoutine(Routine):
    """A base routine that has output functionality"""
    def __init__(self, output_dir):
        Routine.__init__(self)
        self._output_dir = output_dir

    def initialize(self):
        if not os.path.exists(self._output_dir):
            print '[INFO] Path %s does not exist, creating ...' % self._output_dir
            os.makedirs(self._output_dir)

    def save_data(self, data):
        tod_id = self.get_context().get_id()
        with open(self._output_dir+str(tod_id)+".pickle", "w") as f:
            cPickle.dump(data, f, cPickle.HIGHEST_PROTOCOL)
            print '[INFO] Data saved: %s' % self._output_dir+str(tod_id)+".pickle"

    def save_figure(self, fig):
        tod_id = self.get_context().get_id()
        fig.savefig(self._output_dir+str(tod_id)+".png")

    def finalize(self):
        # write metadata to the directory
        metadata = self.get_context().get_metadata()
        if metadata:  # if metadata exists
            with open(self._output_dir+".metadata", "w") as f:
                cPickle.dump(metadata, f, cPickle.HIGHEST_PROTOCOL)


class SaveData(OutputRoutine):
    """A routine to save data from data store"""
    def __init__(self, input_key, output_dir):
        OutputRoutine.__init__(self, output_dir)
        self._input_key = input_key

    def execute(self):
        data = self.get_context().get_store().get(self._input_key)
        self.save_data(data)


class Logger(Routine):
    """A routine to log a key, for debugging purpose"""
    def __init__(self, input_key):
        Routine.__init__(self)
        self._input_key = input_key

    def initialize(self):
        self._pp = pprint.PrettyPrinter(indent=1)
        
    def execute(self):
        data = self.get_store().get(self._input_key)
        print '[INFO] Logger: %s = ' % self._input_key
        self._pp.pprint(data)



class DataLoader(Routine):
    """A routine that load the saved coincident signals"""
    def __init__(self, input_dir=None, postfix="pickle", output_key="data"):
        """
        :param input_dir:  string
        :param postfix:    string - file extension
        :param output_key: string - key used to store loaded data
        """
        self._input_dir = input_dir
        self._postfix = postfix
        self._output_key = output_key
        self._metadata = None

    def initialize(self):
        self.load_metadata()

    def execute(self):
        """A function that fetch a batch of files in order"""
        i = self.get_id()
        filepath = "%s%s.%s" % (self._input_dir, i, self._postfix)
        if os.path.isfile(filepath):
            with open(filepath, "r") as f:
                data = cPickle.load(f)
                print '[INFO] Fetched: %s' % filepath
                if data:  # check if data is None
                    self.get_store().set(self._output_key, data)
                else:  # data is None
                    print '[WARNING] Data is None, skipping ...'
                    self.veto()  # skipping
        else:
            print '[WARNING] Not found: %s, skipping ...' % filepath
            self.veto()

    def load_metadata(self):
        """Load metadata if there is one"""
        metadata_path = self._input_dir + ".metadata"
        if os.path.isfile(metadata_path):
            print '[INFO] Metadata found!'
            with open(self._input_dir + ".metadata", "r") as meta:
                self._metadata = cPickle.load(meta)
                print '[INFO] Metadata loaded!'

    def get_metadata(self):
        return self._metadata
