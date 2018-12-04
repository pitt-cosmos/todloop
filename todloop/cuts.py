import moby2

from .routines import OutputRoutine
from .base import Routine

class CompileCuts(OutputRoutine):
    """A routine that compile cuts"""
    def __init__(self, input_key, glitchp, output_dir):
        OutputRoutine.__init__(self, output_dir)
        self._input_key = input_key
        self._glitchp = glitchp

    def execute(self, store):
        self.logger.info('Finding glitches...')
        tod_data = store.get(self._input_key)  # retrieve tod_data
        glitch_cuts = moby2.tod.get_glitch_cuts(tod=tod_data, params=self._glitchp)
        self.logger.info('Finding glitches complete')

        # Save into pickle file
        cut_data = {
            "TOD": self.get_context().get_name(),
            "glitch_param": self._glitchp,  # save the parameters used to generate
            "cuts": glitch_cuts,  # save the cuts
            "nsamps": tod_data.nsamps
        }
        self.save_data(cut_data)


class CleanTOD(Routine):
    def __init__(self, tod_key, output_key):
        """This routine remove the MCE cuts and detrend and remove the mean
        for each TOD to prepare for cut compilation

        Parameters:
            tod_key: container of input tod in the store
            output_key: container of output tod in the store
        """
        self._tod_key = tod_key 
        self._output_key = output_key

    def execute(self, store):
        store.logger.info('Cleaning TOD ...')
        tod = store.get(self._tod_container)

        # remove mce cuts
        mce_cuts = moby2.tod.get_mce_cuts(tod)
        moby2.tod.fill_cuts(tod, mce_cuts, no_noise=True)

        # clean data
        moby2.tod.remove_mean(tod)
        moby2.tod.detrend_tod(tod)

        # export to data store
        store.set(self._output_key, tod)
