import os
import pickle
import numpy as np
import pprint

from .base import Routine


class OutputRoutine(Routine):
    """A base routine that has output functionality"""
    def __init__(self, output_dir):
        Routine.__init__(self)
        self._output_dir = output_dir

    def initialize(self):
        if not os.path.exists(self._output_dir):
            self.logger.info('Path %s does not exist, creating ...' % self._output_dir)
            os.makedirs(self._output_dir)

    def save_data(self, data):
        tod_id = self.get_context().get_id()
        filename = os.path.join(self._output_dir, '%d.pickle' % tod_id)
        with open(filename, "w") as f:
            pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
            self.logger.info('Data saved: %s' % filename)

    def save_figure(self, fig):
        tod_id = self.get_context().get_id()
        filename = os.path.join(self._output_dir, '$d.png' % tod_id)
        fig.savefig(filename)
        self.logger.info('Figure saved: %s' % filename)

    def finalize(self):
        # write metadata to the directory
        metadata = self.get_context().get_metadata()
        if metadata:  # if metadata exists
            filename = os.path.join(self._output_dir, '.metadata')
            with open(filename, "w") as f:
                pickle.dump(metadata, f, pickle.HIGHEST_PROTOCOL)
                self.logger.info("Metadata is saved at: %s", filename)


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
        self.logger.info("Logger: %s = ' % self._input_key")
        self._pp.pprint(data)


class DataLoader(Routine):
    """A routine that load the saved coincident signals"""
    def __init__(self, input_dir=None, postfix="pickle", output_key="data"):
        """
        :param input_dir:  string
        :param postfix:    string - file extension
        :param output_key: string - key used to store loaded data
        """
        Routine.__init__(self)
        self._input_dir = input_dir
        self._postfix = postfix
        self._output_key = output_key
        self._metadata = None

    def initialize(self):
        self.load_metadata()

    def execute(self):
        """A function that fetch a batch of files in order"""
        i = self.get_id()
        filepath = os.path.join(self._input_dir, "%s.%s" % (i, self._postfix))
        if os.path.isfile(filepath):
            with open(filepath, "r") as f:
                if self._postfix == "pickle":
                    data = pickle.load(f)
                elif self._postfix == "npy":
                    data = np.load(f)
                else:
                    self.logger.error("Unrecognized mode!")
                    self.veto()
                    return

                self.logger.info('Fetched: %s' % filepath)
                if len(data)>0:  # check if data is None
                    self.get_store().set(self._output_key, data)
                else:  # data is None
                    self.logger.warn('Data is None, skipping ...')
                    self.veto()  # skipping
        else:
            self.logger.warn('Not found: %s, skipping ...' % filepath)
            self.veto()

    def load_metadata(self):
        """Load metadata if there is one"""
        metadata_path = self._input_dir + ".metadata"
        if os.path.isfile(metadata_path):
            self.logger.info('Metadata found!')
            filename = os.path.join(self._input_key, '.metadata')
            with open(filename, "r") as meta:
                self._metadata = pickle.load(meta)
                self.logger.info('Metadata loaded from: %s!' % filename)

    def get_metadata(self):
        return self._metadata
