import numpy as np

from .routines import OutputRoutine
from .utils.cuts import remove_overlap_tod, trim_edge_cuts, merge_cuts, common_cuts, find_peaks
from .utils.pixels import PixelReader


class FindCosigs(OutputRoutine):
    """A routine that compiles the coincident signals from cuts"""

    def __init__(self, season="2016", input_key="cuts",
                 output_key="cosig", output_dir="outputs/cosigs",
                 strict=True, polarized=False, save=True):
        """
        :param input_key: string
        :param output_key: string
        :param strict: boolean - Strict mode means each pixel must have 4 TES
                       detectors. Loose mode means that each frequency has at
                       least one TES detectors.
        :param polarized: boolean - True means that we are looking for potentially
                        polarized signals. False means that we only look for
                        un-polarized signals.
        """
        OutputRoutine.__init__(self, output_dir)
        self._input_key = input_key
        self._output_key = output_key
        self._pr = None
        self._strict = strict
        self._polarized = polarized
        self._season = season
        self._save = save

    def execute(self, store):
        # retrieve all cuts
        self._pr = PixelReader(season=self._season, array=self.get_context().get_array())
        cuts_data = store.get(self._input_key)  # get saved cut data
        cuts = cuts_data['cuts']
        nsamps = cuts_data['nsamps']

        # get all pixels
        pixels = self._pr.get_pixels()

        # initialize dictionary to store coincident signals
        cosig = {}

        # loop through pixels and find cosig for each pixel
        for p in pixels:
            dets_f1 = self._pr.get_f1(p)
            dets_f2 = self._pr.get_f2(p)

            if self._strict:  # strict mode, 4 TES have to be present
                if len(dets_f1) == 2 and len(dets_f2) == 2:
                    cuts_f1_A = cuts.cuts[dets_f1[0]]  # low freq, polarization A
                    cuts_f1_B = cuts.cuts[dets_f1[1]]  # low freq, polarization B

                    cuts_f2_A = cuts.cuts[dets_f2[0]]  # high freq, polarization A
                    cuts_f2_B = cuts.cuts[dets_f2[1]]  # high freq, polarization B

                    if self._polarized:  # if looking for polarized, glitch may occur in either polarization
                        cuts_f1 = merge_cuts(cuts_f1_A, cuts_f1_B)  # polarized spikes may appear at either pol
                        cuts_f2 = merge_cuts(cuts_f2_A, cuts_f2_B)

                    else:  # if looking for unpolarized, glitch must occur in both polarizations
                        cuts_f1 = common_cuts(cuts_f1_A, cuts_f1_B)  # unpolarized spikes appear in both pols
                        cuts_f2 = common_cuts(cuts_f2_A, cuts_f2_B)

                    cosig[str(p)] = common_cuts(cuts_f1, cuts_f2)  # store coincident signals by pixel id

            else:  # loose mode, at least one TES has to be present each freq
                if len(dets_f1) == 2 and len(dets_f2) == 2:
                    cuts_f1_A = cuts.cuts[dets_f1[0]]  # low freq, polarization A
                    cuts_f1_B = cuts.cuts[dets_f1[1]]  # low freq, polarization B

                    cuts_f2_A = cuts.cuts[dets_f2[0]]  # high freq, polarization A
                    cuts_f2_B = cuts.cuts[dets_f2[1]]  # high freq, polarization B

                    if self._polarized:  # if looking for polarized, glitch may occur in either polarization
                        cuts_f1 = merge_cuts(cuts_f1_A, cuts_f1_B)  # polarized spikes may appear at either pol
                        cuts_f2 = merge_cuts(cuts_f2_A, cuts_f2_B)

                    else:  # if looking for unpolarized, glitch must occur in both polarizations
                        cuts_f1 = common_cuts(cuts_f1_A, cuts_f1_B)  # unpolarized spikes appear in both pols
                        cuts_f2 = common_cuts(cuts_f2_A, cuts_f2_B)

                    cosig[str(p)] = common_cuts(cuts_f1, cuts_f2)  # store coincident signals by pixel id

                elif len(dets_f1) == 1 and len(dets_f2) == 2:
                    cuts_f1 = cuts.cuts[dets_f1[0]]  # low freq, polarization A

                    cuts_f2_A = cuts.cuts[dets_f2[0]]  # high freq, polarization A
                    cuts_f2_B = cuts.cuts[dets_f2[1]]  # high freq, polarization B

                    if self._polarized:  # if looking for polarized, glitch may occur in either polarization
                        cuts_f2 = merge_cuts(cuts_f2_A, cuts_f2_B)

                    else:  # if looking for unpolarized, glitch must occur in both polarizations
                        cuts_f2 = common_cuts(cuts_f2_A, cuts_f2_B)

                    cosig[str(p)] = common_cuts(cuts_f1, cuts_f2)  # store coincident signals by pixel id

                elif len(dets_f1) == 2 and len(dets_f2) == 1:
                    cuts_f1_A = cuts.cuts[dets_f1[0]]  # low freq, polarization A
                    cuts_f1_B = cuts.cuts[dets_f1[1]]  # low freq, polarization B

                    cuts_f2 = cuts.cuts[dets_f2[0]]  # high freq, polarization A

                    if self._polarized:  # if looking for polarized, glitch may occur in either polarization
                        cuts_f1 = merge_cuts(cuts_f1_A, cuts_f1_B)

                    else:  # if looking for unpolarized, glitch must occur in both polarizations
                        cuts_f1 = common_cuts(cuts_f1_A, cuts_f1_B)

                    cosig[str(p)] = common_cuts(cuts_f1, cuts_f2)  # store coincident signals by pixel id

                elif len(dets_f1) == 1 and len(dets_f2) == 1:
                    cuts_f1 = cuts.cuts[dets_f1[0]]  # low freq, polarization A
                    cuts_f2 = cuts.cuts[dets_f2[0]]  # high freq, polarization A

                    cosig[str(p)] = common_cuts(cuts_f1, cuts_f2)  # store coincident signals by pixel id

        # cosig may contain empty cut vectors because we didn't enforce it, filter them out now
        cosig_filtered = {}
        for pixel in cosig:
            cuts = cosig[pixel]
            if len(cuts) != 0:
                cosig_filtered[pixel] = cuts

        # save cosig for further processing
        store.set(self._output_key, cosig_filtered) 

        # save
        if self._save:
            self.save_data(cosig_filtered)
        
