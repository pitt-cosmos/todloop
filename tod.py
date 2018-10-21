import moby2
from moby2.scripting import get_filebase
from base import Routine
import pandas as pd


class TODLoader(Routine):
    def __init__(self, output_key="tod_data", abspath=False):
        """
        A routine that loads the TOD and save it to a key
        :param output_key: string - key used to save the tod_data
        :param abspath: bool - if the input name is absolute path or just name
        """
        Routine.__init__(self)
        self._output_key = output_key
        self._fb = None
        self._abspath = abspath

    def initialize(self):
        self._fb = get_filebase()

    def execute(self):
        if self._abspath:  # if absolute path is given
            tod_filename = self.get_name()
        else:
            tod_name = self.get_name()
            tod_filename = self._fb.filename_from_name(tod_name, single=True)  # get file path
        print '[INFO] Loading TOD: %s ...' % tod_filename
        tod_data = moby2.scripting.get_tod({'filename': tod_filename, 'repair_pointing': True})
        print '[INFO] TOD loaded'
        self.get_store().set(self._output_key, tod_data)  # save tod_data in memory for routines to process


class TODInfoLoader(Routine):
    """A routine to load TODInfo"""
    def __init__(self, output_key="tod_info", season='2016', array='AR3'):
        Routine.__init__(self)
        self._tod_info = None
        self._season = season
        self._array = array
        self._output_key = output_key

    def initialize(self):
        self._tod_info = pd.read_csv('../data/s16_pa3_tod_info.csv', header=None)  # TODO: Support more seasons
        self._tod_info.columns = ['TOD', 'hour', 'altitude', 'azimuth', 'PWV', 'cut_status', 'field']

    def execute(self):
        tod_name = self.get_name()
        tod_info_index = list(self._tod_info.index[self._tod_info['TOD']==tod_name])
        if len(tod_info_index) != 0:  # if an entry is found
            tod_info_dict = {}
            for col in self._tod_info.columns:
                tod_info_dict[col] = self._tod_info.iloc[tod_info_index[0]][col]
            print '[INFO] TODInfo found: %s' % tod_info_dict
            self.get_store().set(self._output_key, tod_info_dict)
        else:  # if no entry is found
            print '[WARNING] No TODInfo found with name: %s' % tod_name


class TODSelector(Routine):
    def __init__(self, tod_list):
        """A routine that takes a list of TOD names and run the TODLoop on 
        the given TOD list based on a base list
        :param: 
            tod_list: a list of tods names to run over"""
        Routine.__init__(self)
        self._tod_list = tod_list 
            
    def execute(self):
        """Scripts that run for each TOD"""
        tod_name = self.get_name()
        if tod_name not in self._tod_list:
            self.veto()  # halt subsequent routines



