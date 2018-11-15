import moby2
from todloop.routines import OutputRoutine


class CompileCuts(OutputRoutine):
    """A routine that compile cuts"""
    def __init__(self, input_key, glitchp, output_dir):
        OutputRoutine.__init__(self, output_dir)
        self._input_key = input_key
        self._glitchp = glitchp

    def execute(self):
        self.logger.info('Finding glitches...')
        tod_data = self.get_context().get_store().get(self._input_key)  # retrieve tod_data
        glitch_cuts = moby2.tod.get_glitch_cuts(tod=tod_data, params=self._glitchp)
        mce_cuts = moby2.tod.get_mce_cuts(tod=tod_data)  # get mce cuts
        self.logger.info('Finding glitches complete')

        # Save into pickle file
        cut_data = {
            "TOD": self.get_context().get_name(),
            "glitch_param": self._glitchp,  # save the parameters used to generate
            "cuts": glitch_cuts,  # save the cuts
            "mce": mce_cuts,
            "nsamps": tod_data.nsamps
        }
        self.save_data(cut_data)

